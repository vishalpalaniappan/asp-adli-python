import ast

from injector.helper import getEmptyRootNode
from injector.VariableCollectors.CollectCallVariables import CollectCallVariables

class ValueKeyInjector(ast.NodeTransformer):

    def __init__(self, node, varMap, funcId):
        self.varMap = varMap
        self.funcId = funcId

        if 'body' in node._fields:
            node = getEmptyRootNode(node)
    
        self.generic_visit(node)

    def getVariable(self, name):
        for id in self.varMap:
            v = self.varMap[id]
            if v["name"] == name and (self.funcId == v["funcId"] or v["global"]):
                return v
            
        return None
    
    def insertValueKey(self, node):
        return ast.Subscript(value=node, slice= ast.Constant(value="asp_value"))

    def visit_Name(self,node):
        varInfo = self.getVariable(node.id)
        if varInfo and isinstance(node.ctx, ast.Load):
            node = self.insertValueKey(node)

        return node