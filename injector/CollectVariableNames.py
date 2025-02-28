import ast
import uuid
from injector.helper import getVariableLogStatement

VAR_COUNT = 0

def getVariableInfo(name, keys, syntax):
    global VAR_COUNT
    VAR_COUNT += 1
    var = {
        "varId": VAR_COUNT,
        "name": name,
        "keys": keys,
        "syntax": syntax,
    }
    return var

class CollectVariableInfo(ast.NodeTransformer):

    def __init__(self, node):
        self.keys = []
        self.vars = []
        self.tempVars = []
        self.tempVarStmts = []
        self.generic_visit(self.getModule(node))

        name = self.keys.pop(0)["value"]
        varInfo = getVariableInfo(name, self.keys, ast.unparse(node))
        self.vars.append(varInfo)

        nodes = []
        for assign in self.tempVarStmts:
            nodes.append(assign)
            name = assign.targets[0].id
            varInfo = getVariableInfo(name, [], name)
            self.tempVars.append(varInfo)
            nodes.append(getVariableLogStatement(varInfo["name"], varInfo["varId"]))

        self.tempVarStmts = nodes

    def getInfo(self):
        return [self.vars, self.tempVars, self.tempVarStmts]

    def getModule(self, node):
        return ast.Module(body=[node], type_ignores=[])
    
    def addKey(self, type, value):
        self.keys.append({
            "type": type,
            "value": value
        })
    
    def getAssign(self, node):
        name = "asp_adli_var_" + str(uuid.uuid4()).replace("-", "") 
        assign = ast.Assign (
            targets= [ast.Name(id=name, ctx=ast.Store())],
            value= node
        )
        self.tempVarStmts.append(ast.fix_missing_locations(assign))
        self.addKey("variable", assign.targets[0].id)
        return assign

    def visit_Subscript(self, node):
        if isinstance(node.slice, ast.Attribute):
            self.generic_visit(self.getModule(node.value))
            self.getAssign(node.slice)
        else:
            self.generic_visit(node)
        return node
    
    def visit_Call(self, node):
        self.getAssign(node)
        return node
    
    def visit_Name(self, node):
        self.generic_visit(node)
        self.addKey("key", node.id)
        return node
    
    def visit_Attribute(self, node):
        self.generic_visit(node)
        self.addKey("key", node.attr)
        return node
    
    def visit_Constant(self, node):
        self.generic_visit(node)
        self.addKey("key", node.value)
        return node


def extractVariables(node):
    vars = []
    stmts = []
    tempVars = []

    if isinstance(node, ast.Assign):
        for target in node.targets:
            [_vars, _tempVars, _stmts] = CollectVariableInfo(target).getInfo()
            vars += _vars
            tempVars += _tempVars
            stmts += _stmts
    elif isinstance(node, ast.AnnAssign) and node.value:
        [vars, tempVars, stmts] = CollectVariableInfo(node.target).getInfo()
    elif isinstance(node, ast.AugAssign):
        [vars, tempVars, stmts] = CollectVariableInfo(node.target).getInfo()
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for arg in node.args.args:
            vars.append(getVariableInfo(arg.arg, [], arg.arg))
    
    return [stmts, vars, tempVars]
