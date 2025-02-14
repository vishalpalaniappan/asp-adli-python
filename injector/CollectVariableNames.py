import ast

VAR_COUNT = 0

class CollectVariableNames(ast.NodeVisitor):
    '''
        This class visits each node in the tree and 
        collects the variable names.
    '''
    def __init__(self,node):
        self.vars = []
        self.generic_visit(node)
        
    def addVariable(self, node, name):
        '''
            Add variable to vars list.
        '''
        global VAR_COUNT
        VAR_COUNT += 1
        varInfo = {
            "lineno": node.lineno,
            "end_lineno": node.end_lineno,
            "col_offset": node.col_offset,
            "end_col_offset": node.end_col_offset,
            "varId": VAR_COUNT,
            "name": name
        }
        self.vars.append(varInfo)

    def visit_Name(self,node):
        '''
            Visit name node and save stored variables.
        '''
        if (node.id not in self.vars):
            if isinstance(node.ctx,ast.Store):
                self.addVariable(node, node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        '''
            Visit attribute node and save stored variables.
        '''
        module = ast.Module(body=[node], type_ignores=[])
        syntax = ast.unparse(ast.fix_missing_locations((module)))
        if syntax not in self.vars:
            if isinstance(node.ctx, ast.Store):
                self.addVariable(node, syntax)
        self.generic_visit(node)

    def visit_Subscript(self, node):
        '''
            Visit subscript node and save stored variables.
        '''
        module = ast.Module(body=[node], type_ignores=[])
        syntax = ast.unparse(ast.fix_missing_locations((module)))
        if syntax not in self.vars:
            if isinstance(node.ctx, ast.Store):
                self.addVariable(node, syntax)
        self.generic_visit(node)

    def visit_arg(self, node):
        '''
            Visit arg node and save stored variables.
        '''
        if "arg" in node._fields:
            if node.arg not in self.vars:
                self.addVariable(node, node.arg)
        self.generic_visit(node)