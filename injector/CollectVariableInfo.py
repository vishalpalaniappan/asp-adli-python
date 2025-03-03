import ast
import uuid
from injector.helper import getVarLogStmt, getAssignStmt, getEmptyRootNode

VAR_COUNT = 0

class CollectAssignVarInfo(ast.NodeVisitor):

    def __init__(self, node, logTypeId, funcId):
        self.node = node
        self.logTypeId = logTypeId
        self.funcId = funcId
        self.keys = []
        self.variables = []
        self.generic_visit(ast.Module(body=[node], type_ignores=[]))

        if len(self.keys) > 0:
            name = self.keys.pop(0)["value"]
            self.getVarInfo(name, self.keys, ast.unparse(self.node), None)
        
    def getVariableName(self):
        return "asp_temp_var_" + str(uuid.uuid1()).replace("-", "")
        
    def getVarInfo(self, name, keys, syntax, node):
        global VAR_COUNT
        VAR_COUNT += 1
        self.variables.append({
            "varId": VAR_COUNT,
            "name": name,
            "keys": keys,
            "syntax": syntax,
            "assignValue": node,
            "logType": self.logTypeId,
            "funcId": self.funcId,
            "isTemp": node is not None
        })

    def visit_Subscript(self, node):
        if not isinstance(node.slice, (ast.Constant, ast.Name)):
            self.generic_visit(ast.Module(body=[node.value], type_ignores=[]))

            varName = self.getVariableName()
            self.keys.append({"type": "temp_variable", "value": varName})
            self.getVarInfo(varName, [], varName, node.slice)

            node.slice = ast.Name(id= varName, ctx=ast.Load())
        else:
            self.generic_visit(node)
        return node
    
    def visit_Name(self, node):
        self.generic_visit(node)
        self.keys.append({"type":"variable", "value":node.id})
        return node
    
    def visit_Attribute(self, node):
        self.generic_visit(node)
        self.keys.append({"type":"key", "value":node.attr})
        return node
    
    def visit_Constant(self, node):
        self.generic_visit(node)
        self.keys.append({"type":"key", "value":node.value})
        return node
    

class CollectFunctionArgInfo(ast.NodeVisitor):

    def __init__(self, node, logTypeId, funcId):
        self.variables = []
        self.logTypeId = logTypeId
        self.funcId = funcId
        self.generic_visit(node)

    def getVarInfo(self, name, keys, syntax, node):
        global VAR_COUNT
        VAR_COUNT += 1
        self.variables.append({
            "varId": VAR_COUNT,
            "name": name,
            "keys": keys,
            "syntax": syntax,
            "assignValue": node,
            "logType": self.logTypeId,
            "funcId": self.funcId,
            "isTemp": node is not None
        })
    
    def visit_arg(self, node):
        self.getVarInfo(node.arg, [], node.arg, None)
    

class CollectVariableDefault(ast.NodeVisitor):

    def __init__(self, node, logTypeId, funcId):
        self.variables = []
        self.logTypeId = logTypeId
        self.funcId = funcId

        if 'body' in node._fields:
            emptyNode = getEmptyRootNode(node)
            self.generic_visit(emptyNode)
        else:
            self.generic_visit(node)

    def getVarInfo(self, name, keys, syntax, node):
        global VAR_COUNT
        VAR_COUNT += 1
        self.variables.append({
            "varId": VAR_COUNT,
            "name": name,
            "keys": keys,
            "syntax": syntax,
            "assignValue": node,
            "logType": self.logTypeId,
            "funcId": self.funcId,
            "isTemp": node is not None
        })
    
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.getVarInfo(node.id, [], node.id, None)
        self.generic_visit(node)

    