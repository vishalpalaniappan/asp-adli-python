import ast

def isValidCall(node, callName):
    isName = isinstance(node.func, ast.Name)
    isAttr = isinstance(node.func, ast.Attribute)
    return ((isName and node.func.id == callName) or (isAttr and node.func.attr == callName))

class OutputWrapper(ast.NodeVisitor):

    def __init__(self, node, outputMeta):
        self.node = node
        self.outputMeta = outputMeta
        self.generic_visit(ast.Module(body=[node], type_ignores=[]))
    
    def visit_Call(self, node):
        print(ast.unparse(node))
        for output in self.outputMeta:
            if isValidCall(node, output["function"]):
                print("Found function named", output["function"])

        return node