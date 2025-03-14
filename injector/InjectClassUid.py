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
            self.add_init_method(node)

    def add_assign_stmt(self, node):
        '''
            Add assign statement which sets the value of asp_uid.
        '''
        # TODO: Reimplement this with proper ast construction.
        if_stmt = ast.parse('''if (\"asp_uid\" not in self):
    pass''').body[0]
        
        assign = ast.Assign(
            targets = [ast.Attribute(
                value= ast.Name(id="self", ctx=ast.Store),
                attr= "asp_uid", 
            )],
            value = ast.Constant(value = self.uuid)                
        )

        if_stmt.body[0] = assign
        node.body.insert(0, ast.fix_missing_locations(if_stmt))

    def add_log_uid_stmt(self,node):
        '''
            Adds a statement which logs the unique id at the
            start of the function.
        '''
        logStmt = ast.Expr(
            ast.Call(
                func=ast.Name(id='logger.info', ctx=ast.Load()),
                args=[ast.JoinedStr(
                    values= [
                        ast.Constant(value= "@ "),
                        ast.FormattedValue(
                            value = ast.Attribute(
                                value= ast.Name(id="self", ctx=ast.Load()),
                                attr= "asp_uid", 
                            ),
                            conversion = -1
                        )
                    ]
                )],
                keywords=[]
            )
        )
        node.body.insert(0, ast.fix_missing_locations(logStmt))

    def add_init_method(self, node):
        '''
            Adds an initialization function if it doesn't exist
            in the class.
        '''
        init_method = ast.FunctionDef(
            name='__init__',
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg='self', annotation=None)],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]
            ),
            body=[],
            decorator_list=[],
            returns=None
        )
        self.add_assign_stmt(init_method)

        init_method = ast.fix_missing_locations(init_method)
        node.body.insert(0, init_method)
        

    def visit_FunctionDef(self, node):
        '''
            Add init function or log statement.
        '''
        if (node.name == "__init__"):
            self.has_init = True
            self.add_assign_stmt(node)
        else:
            self.add_log_uid_stmt(node)

        return node