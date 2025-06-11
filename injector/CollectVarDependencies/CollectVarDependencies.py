import ast
import copy
from injector.helper import getEmptyRootNode

class CollectVarDependencies(ast.NodeVisitor):
    def __init__(self, node):
        self.deps = []
        self.vars = []

        if 'body' in node._fields:
            emptyNode = getEmptyRootNode(node)
            self.generic_visit(emptyNode)
        else:
            self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.vars.append(node.id)
        elif isinstance(node.ctx, ast.Load):
            self.deps.append(node.id)
