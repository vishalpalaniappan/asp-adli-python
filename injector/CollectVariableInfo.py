import ast
import uuid

VAR_COUNT = 0

class CollectVariableInfo(ast.NodeTransformer):

    def __init__(self, node):
        self.node = node
        self.keys = []
        self.variables = []
        self.logstmts = []
        self.generic_visit(ast.Module(body=[node], type_ignores=[]))

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
            "node": node,
            "isTemp": node != None
        })

    def visit_Subscript(self, node):
        if not isinstance(node.slice, (ast.Constant, ast.Name)):
            self.generic_visit(ast.Module(body=[node.value], type_ignores=[]))

            varName = self.getVariableName()
            self.keys.append({"type": "temp_variable", "value": varName})
            self.getVarInfo(varName, [], varName, node.slice)

            node.slice = ast.Name(id= varName, ctx=ast.Load)
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