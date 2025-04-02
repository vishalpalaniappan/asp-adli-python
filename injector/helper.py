import ast
import inspect
import copy
import json
import re

from injector.injectedFunctions import varLog

def getRootLoggingSetup(logFileName):
    """
        Returns the root logging setup for the program. 

        Args:
            logFileName: Name of the generated CDL log file.
    """
    nodes = []
    nodes.append(ast.parse("import traceback").body[0])
    nodes.append(ast.parse("import logging").body[0])
    nodes.append(ast.parse("import json").body[0])
    nodes.append(ast.parse("import sys").body[0])
    nodes.append(ast.parse("import uuid").body[0])
    nodes.append(ast.parse("from pathlib import Path").body[0])
    nodes.append(ast.parse("from clp_logging.handlers import CLPFileHandler").body[0])
    s = "clp_handler = CLPFileHandler(Path('{f}'))".format(f='./' + logFileName + '.clp.zst')
    nodes.append(ast.parse(s).body[0])
    nodes.append(ast.parse("logger = logging.getLogger('adli')").body[0])
    nodes.append(ast.parse("logger.setLevel(logging.INFO)").body[0])
    nodes.append(ast.parse("logger.addHandler(clp_handler)").body[0])
    return nodes

def getLoggingSetup():
    """
        Returns the logging setup for any imported files.
    """
    nodes = []
    nodes.append(ast.parse("import logging").body[0])
    nodes.append(ast.parse("import json").body[0])
    nodes.append(ast.parse("import uuid").body[0])
    nodes.append(ast.parse("logger = logging.getLogger('adli')").body[0])
    return nodes

def getLoggingStatement(logStr):
    """
        Returns a logging statement as an AST node.
    """
    return ast.Expr(
        ast.Call(
            func=ast.Name(id='logger.info', ctx=ast.Load()),
            args=[ast.Constant(value=logStr)],
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

def getLtLogStmt(logTypeId):
    '''
        This function returns a logger.info statement with the 
        provided logtype id.
    '''
    return ast.Expr(
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='logger', ctx=ast.Load()),
                attr='info',
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
    logFunction = ast.Call(
            func=ast.Name(id='aspAdliVarLog', ctx=ast.Load()),
            args=[
                ast.Name(id=name, ctx=ast.Load()),
                ast.Constant(value=varId)
            ],
            keywords=[]
        )

    return getAssignStmt(name, logFunction)

def getTraceIdLogStmt(traceType, variable):
    '''
       Returns a log statement for trace ids.
    '''
    return ast.Expr(
        value=ast.Call(
            func=ast.Name(id='aspTraceLog', ctx=ast.Load()),
            args=[
                ast.Constant(value=traceType),
                ast.Name(id=variable, ctx=ast.Load()),
            ],
            keywords=[]
        )
    )

def getEmptyRootNode(astNode):
    '''
        Removes all child nodes from astnode. This is used to 
        extract the variables without visiting the child nodes.
    '''
    node = copy.copy(astNode)
    keysToEmpty = ["body", "orelse","else","handlers","finalbody"]
    for key in keysToEmpty:
        if key in node._fields:
            setattr(node, key, [])
    return node

def getLoggingFunction():
    ''' 
       Returns a function used to log variables.
    '''
    body = ast.parse(inspect.getsource(varLog)).body
    body[0].name = "aspAdliVarLog"
    return body

def injectRootLoggingSetup(tree, header, fileName):
    '''
        Injects try except structure around the given tree.
        Injects root logging setup and function the given tree.
    '''
    handler = ast.ExceptHandler(
        type=ast.Name(id='Exception', ctx=ast.Load()),
        name='e',
        body=[
            ast.parse("logger.error(f\"? {traceback.format_exc()}\")"),
            ast.parse("raise"),
        ]
    )

    mainTry = ast.Try(
        body=tree.body,
        handlers=[handler],
        orelse=[],
        finalbody=[]
    )
    rootLoggingSetup = getRootLoggingSetup(fileName)
    loggingFunction = getLoggingFunction()
    header = getLoggingStatement(json.dumps(header))

    mod = ast.Module(body=[], type_ignores=[])
    mod.body = rootLoggingSetup + loggingFunction + [header] + [mainTry]
    return mod

def injectLoggingSetup(tree):
    '''
        Injects logging setup and function into the provided tree.
    '''
    loggingSetup = getLoggingSetup()
    loggingFunction = getLoggingFunction()
    mod = ast.Module(body=[], type_ignores=[])
    mod.body = loggingSetup + loggingFunction + tree.body
    return mod

def getDisabledVariables(node):
    """
        This function parses the variable disable comments and returns
        a list with the disabled variable names.

        Currently, the python AST library only supports parsing triple
        quote comments. 

        Example:
        '''adli-disable-variable varName1 varName2 varNameN'''
    """
    
    disabledVariables = []
    if "value" in node._fields and isinstance(node.value, ast.Constant):

        value = node.value.value
        variables = re.findall("adli-disable-variable (.*)", value)

        if len(variables) > 0:
            disabledVariables = variables[0].split()
        
    return disabledVariables
