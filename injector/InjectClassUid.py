import ast
import uuid

class InjectClassUid(ast.NodeTransformer):
    '''
        Injects a UID into the class. If no initialization function
        exists, it adds it.
    '''
    
    def __init__(self, node):

        if isinstance(node, ast.ClassDef):
            self.uuid = str(uuid.uuid4())
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
                value = ast.Constant(value = self.uuid)                
            ))
            node.body.insert(0, assign)
        else:
            logStmt = ast.Expr(
                ast.Call(
                    func=ast.Name(id='logger.info', ctx=ast.Load()),
                    args=[ast.JoinedStr(
                        values= [
                            ast.Constant(value= "@ "),
                            ast.FormattedValue(
                                value = ast.Attribute(
                                    value= ast.Name(id="self", ctx=ast.Store),
                                    attr= "asp_uid", 
                                ),
                                conversion = -1
                            )
                        ]
                    )],
                    keywords=[]
                )
            )
            node.body.insert(0, logStmt)

        return node