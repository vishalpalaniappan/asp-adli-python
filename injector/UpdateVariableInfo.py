import ast

class UpdateVariableInfo(ast.NodeTransformer):
    '''
        This class replaces any variable names with its 
        value for the key named "value". 
        
        Example:
        --------
        a = b + 1
        becomes
        a = b["value"] + 1

        This is because when b was assigned a value, a uid 
        was generated to identify the unique instance of 
        the variable. 
    '''    
    
    def __init__(self, node, varNames):
        # varNames is list of variable names in the current scope.
        self.varNames = varNames
        self.generic_visit(node)

    def visit_Name(self, node):
        '''
            Replaces variable with its value at the "value" key
        '''
        if node.id in self.varNames and isinstance(node.ctx, ast.Load):
            node = ast.Subscript(
                value = node.id,
                slice = ast.Constant(
                    value= "value"
                ),
                ctx = ast.Load                
            )

        return node