import ast
import copy
import json


def getInjectedImports():
    """
        Imports the adliLogger instance
    """
    return [
        ast.ImportFrom(
            module="AdliLogger",
            names = [
                ast.alias(name="adli")
            ],
            level=0
        )
    ]

def getHeaderLogStmt():
    """
        Returns a logging statement as an AST node.
    """
    return ast.Expr(
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='adli', ctx=ast.Load()),
                attr='logHeader',
                ctx=ast.Load()
            ),
            args=[],
            keywords=[]
        )
    )

def getLtLogStmt(logTypeId):
    '''
        This function returns a logger.info statement with the 
        provided logtype id.
    '''
    return ast.Expr(
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='adli', ctx=ast.Load()),
                attr='logStmt',
                ctx=ast.Load()
            ),
            args=[
                ast.Constant(value=logTypeId),
                ast.Name(id="adli_uid", ctx=ast.Load()),
                ast.Call(
                    func=ast.Attribute(
                        value= ast.Attribute(
                            value=ast.Name(id='adli', ctx=ast.Load()),
                            attr='traceback',
                            ctx=ast.Load()
                        ),
                        attr='extract_stack',
                        ctx=ast.Load()
                    ),
                    args=[],
                    keywords=[]
                )
            ],
            keywords=[]
        )
    )

def getVarLogStmt(name, varId):
    '''
        Returns a function call to log the given variables.
    '''
    logVariableCall = ast.Call(
        func=ast.Attribute(
            value=ast.Name(id='adli', ctx=ast.Load()),
            attr='logVariable',
            ctx=ast.Load()
        ),
        args=[
            ast.Constant(value=varId),
            ast.Name(id=name, ctx=ast.Load()),
            ast.Name(id="adli_uid", ctx=ast.Load()),
        ],
        keywords=[]
    )

    return getAssignStmt(name, logVariableCall)

def getAssignStmt(name, value):
    '''
        Returns an assign statement with the provided arguments.
    '''
    return ast.fix_missing_locations(ast.Assign(
        targets=[ast.Name(id=name, ctx=ast.Store)],
        value= value
    ))

def getEmptyRootNode(astNode):
    '''
        Removes all child nodes from astnode. This is used to 
        extract the variables without visiting the child nodes.
        For example, with a for loop like: `for i in range(n)`
    '''
    node = copy.copy(astNode)
    keysToEmpty = ["body", "orelse","else","handlers","finalbody"]
    for key in keysToEmpty:
        if key in node._fields:
            setattr(node, key, [])
    return node

def injectRootLoggingSetup(tree):
    '''
        Injects try except structure around the given tree.
        Injects header into file and imports adli logger instance.
    '''
    handler = ast.ExceptHandler(
        type=ast.Name(id='Exception', ctx=ast.Load()),
        name='e',
        body=[
            ast.parse("adli.logException()"),
            ast.parse("raise"),
        ]
    )

    mainTry = ast.Try(
        body=tree.body,
        handlers=[handler],
        orelse=[],
        finalbody=[]
    )
    loggerInstance = getInjectedImports()
    header = getHeaderLogStmt()

    mod = ast.Module(body=[], type_ignores=[])
    mod.body = loggerInstance + [header] + [mainTry]
    return mod

def injectLoggingSetup(tree):
    '''
        Injects logging setup and function into the provided tree.
    '''
    loggerInstance = getInjectedImports()
    mod = ast.Module(body=[], type_ignores=[])
    mod.body = [loggerInstance] + tree.body
    return mod

def getEncodedOutputStmt(name):
    '''
        Returns an assign statement with the provided arguments.
    '''
    return ast.fix_missing_locations(ast.Assign(
        targets=[ast.Name(id=name, ctx=ast.Store)],
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='adli', ctx=ast.Load()),
                attr='encodeOutput',
                ctx=ast.Load()
            ),
            args=[
                ast.Constant(value=name),
                ast.Name(id=name, ctx=ast.Load())
            ],
            keywords=[]
        )
    ))

def getAdliConfiguration(node):
    """
        Checks to see if the node contains valid ADLI configuration info.
        Return configuration if it is valid and return None if isn't.    

        Example:
        '''
        {
            "type":"adli_disable_variable",
            "value":["parsed_args", "uid"]
        }
        '''
        '''
            {
                "type": "adli_metadata",
                "value": {
                    "name": "ADLI",
                    "description": "A tool to inject diagnostic logs into a python program.",
                    "version": "0.0",
                    "language": "python"
                
                }
            }
        '''
    """

    validCommentTypes = ["adli_disable_variable","adli_metadata","adli_encode_output"]   

    if "value" in node._fields and isinstance(node.value, ast.Constant):     
        comment = node.value.value
        try:
            obj = json.loads(comment)
        except:
            return None

        hasType = "type" in obj 
        hasValue = "value" in obj

        # check if the object has valid type, value and comment type
        if (hasType and hasValue and obj["type"] in validCommentTypes): 
            return obj
            
        return None
    

def getUniqueIdAssignStmt():
    '''
        This function returns an assign statement generates a unique
        and saves it in a variable named asp_uid.

        adli_uid = uuid.uuid4()
    '''

    getUidCall = ast.Call(
        func=ast.Attribute(
            value=ast.Name(id='adli', ctx=ast.Load()),
            attr='getUniqueId',
            ctx=ast.Load()
        ),
        args=[],
        keywords=[]
    )
    
    return ast.fix_missing_locations(ast.Assign(
        targets=[ast.Name(id='adli_uid', ctx=ast.Store())],
        value=getUidCall
    ))

def getRootUidAssign():
    '''
        Returns an assign statement with the provided arguments.
    '''
    return ast.fix_missing_locations(ast.Assign(
        targets=[ast.Name(id='adli_uid', ctx=ast.Store())],
        value= ast.Constant("global")
    ))
