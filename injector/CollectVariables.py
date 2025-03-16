import ast
from injector.helper import getEmptyRootNode

class CollectVariables(ast.NodeVisitor):
    '''
        Base class for collecting var info and generation var info object.
    '''
    var_count = 0

    def __init__(self, node, logTypeId, funcId, existingVars):
        self.variables = []
        self.logTypeId = logTypeId
        self.funcId = funcId
        self.existingVars = existingVars

        if 'body' in node._fields:
            node = getEmptyRootNode(node)

        self.generic_visit(ast.Module(body=[node],type_ignores=[]))
    
    def getVarInfo(self, name):
        '''
            Appends varinfo object to the variables list.
        '''
        CollectVariables.var_count += 1
        info = {
            "varId": CollectVariables.var_count,
            "name": name,
            "logType": self.logTypeId,
            "funcId": self.funcId,
        }
        self.variables.append(info)

    def isValidVariable(self, name):
        for key in self.existingVars:
            if self.existingVars[key]["name"] == name:
                return True
        return False

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.getVarInfo(node.id)
        self.generic_visit(node)


    def visit_FunctionDef(self, node):
        for childNode in ast.walk(node):
            if isinstance(childNode,ast.arg):
                self.getVarInfo(childNode.arg)

        self.generic_visit(node)

    def visit_Call(self,node):
        for childNode in ast.walk(node):
            if isinstance(childNode,ast.Name) and self.isValidVariable(childNode.id):
                self.getVarInfo(childNode.id)
        self.generic_visit(node)
