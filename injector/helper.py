import ast
import copy
import json


def getAdliLoggerInstance():
    """
        Imports the adliLogger instance
    """
    return ast.ImportFrom(
        module="AdliLogger",
        names = [
            ast.alias(name="adli")
        ],
        level=0
    )

def getHeaderLogStmt(header):
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
            args=[ast.Constant(value=header)],
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
            args=[ast.Constant(value=logTypeId)],
            keywords=[]
        )
    )

def getVarLogStmt(name, varId):
    '''
        Returns a function call to log the given variables.
    '''
    return ast.Expr(
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='adli', ctx=ast.Load()),
                attr='logVariable',
                ctx=ast.Load()
            ),
            args=[
                ast.Constant(value=varId),
                ast.Name(id=name, ctx=ast.Load())
            ],
            keywords=[]
        )
    )

def getAssignStmt(name, value):
    '''
        Returns an assign statement with the provided arguments.
    '''
    return ast.fix_missing_locations(ast.Assign(
        targets=[ast.Name(id=name, ctx=ast.Store)],
        value=value
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

def injectRootLoggingSetup(tree, header, fileName):
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
    loggerInstance = getAdliLoggerInstance()
    header = getHeaderLogStmt(json.dumps(header))

    mod = ast.Module(body=[], type_ignores=[])
    mod.body = [loggerInstance] + [header] + [mainTry]
    return mod

def injectLoggingSetup(tree):
    '''
        Injects logging setup and function into the provided tree.
    '''
    loggerInstance = getAdliLoggerInstance()
    mod = ast.Module(body=[], type_ignores=[])
    mod.body = [loggerInstance] + tree.body
    return mod
