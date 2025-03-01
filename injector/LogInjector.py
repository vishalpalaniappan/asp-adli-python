import ast

class LogInjector(ast.NodeTransformer):
    def __init__(self, node):
        self.generic_visit(node)

    def visit_Assign(self, node):
        return [node, node]