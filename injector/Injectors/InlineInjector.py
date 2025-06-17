import ast
from injector.VariableCollectors.CollectVariableDefault import CollectVariableDefault
from injector.helper import getEmptyRootNode

from injector.helper import getVarLogStmt, getLtLogStmt

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
        variables = CollectVariableDefault(node, self.logTypeId, self.funcId).variables
        self.variables += variables

        elts = [
            getLtLogStmt(self.logTypeId),
            node.elt
        ]

        for variable in variables:
            stmt = getVarLogStmt(variable["syntax"], variable["varId"])
            stmt = stmt.value
            elts.append(stmt)

        node.elt = ast.Subscript(
            value=ast.Tuple(
                elts=elts, ctx= ast.Load()),
            slice= ast.Constant(1),
            ctx= ast.Load()
        )
        return node
    
    def visit_Lambda(self, node):    
        variables = CollectVariableDefault(node, self.logTypeId, self.funcId).variables
        self.variables += variables

        elts = [
            getLtLogStmt(self.logTypeId),
            node.body
        ]

        for variable in variables:
            stmt = getVarLogStmt(variable["syntax"], variable["varId"])
            stmt = stmt.value
            elts.append(stmt)

        node.body = ast.Subscript(
            value=ast.Tuple(
                elts=elts, ctx= ast.Load()),
            slice= ast.Constant(1),
            ctx= ast.Load()
        )
        return node
