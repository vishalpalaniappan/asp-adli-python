import ast

class CollectVariableNames(ast.NodeVisitor):
    '''
        This class visits each node in the tree and 
        collects the variable names.
    '''
    def __init__(self,node):
        self.var_names = []
        self.generic_visit(node)

    def visit_Name(self,node):
        '''
            Visit name node and keep walking.
        '''
        if (node.id not in self.var_names):
            if isinstance(node.ctx,ast.Store):
                self.var_names.append(node.id)
        self.generic_visit( node)

    def visit_Attribute(self, node):
        '''
            Visit attribute node and keep walking.
        '''
        module = ast.Module(body=[node], type_ignores=[])
        syntax = ast.unparse(ast.fix_missing_locations((module)))
        if (syntax not in self.var_names):
            if isinstance(node.ctx, ast.Store):
                self.var_names.append(syntax)
        self.generic_visit(node)

    def visit_Subscript(self, node):
        '''
            Visit subscript node and keep walking.
        '''
        module = ast.Module(body=[node], type_ignores=[])
        syntax = ast.unparse(ast.fix_missing_locations((module)))
        if (syntax not in self.var_names):
            if isinstance(node.ctx, ast.Store):
                self.var_names.append(syntax)
        self.generic_visit(node)

    def visit_arg(self, node):
        '''
            Visit arg node and keep walking.
        '''
        if("arg" in node._fields):
            self.var_names.append(node.arg)
        self.generic_visit(node)