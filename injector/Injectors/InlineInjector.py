import ast
from injector.VariableCollectors.CollectVariableDefault import CollectVariableDefault
from injector.helper import getEmptyRootNode

from injector.helper import getVarLogStmt, getLtLogStmt, getUniqueIdNamedAssignStmt, getLocalVarsLogStmt

class InlineInjector(ast.NodeTransformer):
    
    def __init__(self, node, logTypeId, funcId):

        self.node = node
        self.logTypeId = logTypeId
        self.funcId = funcId
        self.variables = []

        if 'body' in node._fields:
            node = getEmptyRootNode(node)

        self.generic_visit(node)
        

    def visit_GeneratorExp(self, node): 
        self.generic_visit(node)       
        variables = CollectVariableDefault(node, self.logTypeId, self.funcId).variables
        self.variables += variables
        
        elts = [
            getUniqueIdNamedAssignStmt(),
            getLocalVarsLogStmt(),
        ]

        elts = elts + [
            getLtLogStmt(self.logTypeId),
            node.elt
        ]

        node.elt = ast.Subscript(
            value=ast.Tuple(
                elts=elts, ctx= ast.Load()),
            slice= ast.Constant(-1),
            ctx= ast.Load()
        )

        return node
    
    def visit_Lambda(self, node): 
        self.generic_visit(node)   
        variables = CollectVariableDefault(node, self.logTypeId, self.funcId).variables
        self.variables += variables

        elts = [
            getUniqueIdNamedAssignStmt(),
            getLocalVarsLogStmt(),
        ]

        elts = elts + [
            getLtLogStmt(self.logTypeId),
            node.body
        ]

        node.body = ast.Subscript(
            value=ast.Tuple(elts=elts, ctx= ast.Load()),
            slice= ast.Constant(-1),
            ctx= ast.Load()
        )
        return node
