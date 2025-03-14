import ast
import uuid

class InjectClassUid(ast.NodeTransformer):
    '''
        Injects a UID into the class. If no initialization function
        exists, it adds it.
    '''
    
    def __init__(self, node):
        self.functions = []
        self.generic_visit(node)
            

    def visit_FunctionDef(self, node):
        '''
            Initializes uuid value in __init__ function
        '''
        if (node.name == "__init__"):
            assign = ast.fix_missing_locations(ast.Assign(
                targets = [ast.Attribute(
                    value= ast.Name(id="self", ctx=ast.Store),
                    attr= "asp_uid", 
                )],
                value = ast.Constant(value= str(uuid.uuid4()))                
            ))
            node.body.insert(0, assign)

        self.functions.append(node.name)
        return node