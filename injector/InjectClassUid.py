import ast
import uuid

class InjectClassUid(ast.NodeTransformer):
    '''
        Injects a UID into the class. If no initialization function
        exists, it adds it.
    '''
    
    def __init__(self, node):
        self.uuid = str(uuid.uuid4())
        self.has_init = False
        self.generic_visit(node)

        # If the class doesn't have an __init__ method, add one
        if isinstance(node, ast.ClassDef) and not self.has_init:
            init_method = ast.FunctionDef(
                name='__init__',
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg='self', annotation=None)],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[]
                ),
                body=[
                    ast.Assign(
                        targets=[ast.Attribute(
                            value=ast.Name(id='self', ctx=ast.Load),
                            attr='asp_uid',
                        )],
                        value=ast.Constant(value=self.uuid)
                    )
                ],
                decorator_list=[],
                returns=None
            )
            init_method = ast.fix_missing_locations(init_method)
            node.body.insert(0, init_method)
            

    def visit_FunctionDef(self, node):
        '''
            Initializes uuid value in __init__ function
        '''
        if (node.name == "__init__"):
            self.has_init = True
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
                                    value= ast.Name(id="self", ctx=ast.Load),
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