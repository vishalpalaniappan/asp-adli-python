import ast

class FunctionCallCollector(ast.NodeVisitor):
    '''
        Given a statement, this class extracts all the 
        function calls that were made. 
        
        Ex: print(bar(baz(2)), qux())
        Calls: ['print', 'bar', 'baz', 'qux']    
    '''
    def __init__(self, node):
        self.funcNames = []
        self.generic_visit(ast.Module(body=[node], type_ignores=[]))

    def visit_Call(self, node):
        funcName = self.getFuncName(node.func)
        if funcName:
            self.funcNames.append(funcName)
        self.generic_visit(node)

    def getFuncName(self, func_node):
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            return func_node.attr
        return None 