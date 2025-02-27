import ast

VAR_COUNT = 0

class CollectVariable(ast.NodeVisitor):

    def __init__(self, node):
        self.keys = []
        self.vars = []
        self.generic_visit(self.getModule(node))

    def getModule(self, node):
        return ast.Module(body=[node], type_ignores=[])

    def visit_Assign(self, node):
        for target in node.targets:
            self.keys = []
            self.generic_visit(self.getModule(target))
            self.saveVariableInfo(target, self.keys, ast.unparse(target))
        return node

    def visit_AnnAssign(self, node):
        self.keys = []
        self.generic_visit(self.getModule(node.target))
        self.saveVariableInfo(node, self.keys, ast.unparse(node.target))
        return node

    def visit_AugAssign(self, node):
        self.keys = []
        self.generic_visit(self.getModule(node.target))
        self.saveVariableInfo(node, self.keys, ast.unparse(node.target))
        return node
    
    def visit_arg(self, node):
        self.generic_visit(node)
        node.annotation = None
        self.keys.append(node.arg)
        self.saveVariableInfo(node, self.keys, ast.unparse(node))
        return node
    
    def visit_Call(self, node):
        # self.generic_visit(node)
        print("Call:", ast.unparse(node))
        return node
    
    def visit_Name(self, node):
        self.generic_visit(node)
        self.keys.append(node.id)
        return node

    def visit_Constant(self, node):
        self.generic_visit(node)
        self.keys.append(node.value)
        return node

    def visit_Attribute(self, node):
        self.generic_visit(node)
        self.keys.append(node.attr)
        return node

    def saveVariableInfo(self, node, keys, syntax):
        global VAR_COUNT
        VAR_COUNT += 1
        varInfo = {
            "varId": VAR_COUNT,
            "lineno": node.lineno,
            "end_lineno": node.end_lineno,
            "col_offset": node.col_offset,
            "end_col_offset": node.end_col_offset,
            "name": keys.pop(0),
            "keys": keys,
            "syntax": syntax,
        }
        self.vars.append(varInfo)


def extractVariables(node):
    vars = []

    if isinstance(node, ast.Assign):
        vars = CollectVariable(node).vars

    if isinstance(node, ast.AnnAssign) and node.value:
        vars = CollectVariable(node).vars

    if isinstance(node, ast.AugAssign):
        vars = CollectVariable(node).vars

    if isinstance(node, ast.FunctionDef):
        vars = CollectVariable(node).vars
    
    if isinstance(node, ast.AsyncFunctionDef):
        vars = CollectVariable(node).vars
    
    return vars
