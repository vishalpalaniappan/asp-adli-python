import ast
import os
import copy
import json

def checkImport(rootDir, node):
    """
        Given an import statement, this function tests if
        it is a local import and returns the path.
    """
    pathsToCheck = []
    if isinstance(node, ast.Import):
        name = node.names[0].name.replace('.','/')
        path = os.path.join(rootDir, name + '.py')
        pathsToCheck.append(path)
    elif isinstance(node, ast.ImportFrom):
        module = os.path.join(rootDir, node.module.replace('.','/'))
        name = os.path.join(node.names[0].name.replace('.','/'))
        pathsToCheck.append(f"{module}/{name}.py")
        pathsToCheck.append(f"{module}.py")
    
    validPaths = []
    for path in pathsToCheck:
        try:
            open(path)
            validPaths.append(path)
        except Exception as e:
            pass

    return validPaths

def getRootLoggingSetup(logFileName):
    """
        Returns the root logging setup for the program. 

        Args:
            logFileName: Name of the generated CDL log file.
    """
    module = ast.Module(body=[], type_ignores=[])
    module.body.append(ast.parse("import traceback"))
    module.body.append(ast.parse("import logging"))
    module.body.append(ast.parse("import json"))
    module.body.append(ast.parse("import sys"))
    module.body.append(ast.parse("from pathlib import Path"))
    module.body.append(ast.parse("from clp_logging.handlers import CLPFileHandler"))
    s = "clp_handler = CLPFileHandler(Path('{f}'))".format(f='./' + logFileName + '.clp.zst')
    module.body.append(ast.parse(s))
    module.body.append(ast.parse("logger = logging.getLogger('adli')"))
    module.body.append(ast.parse("logger.setLevel(logging.INFO)"))
    module.body.append(ast.parse("logger.addHandler(clp_handler)"))
    return module

def getLoggingSetup():
    """
        Returns the logging setup for any imported files.
    """
    module = ast.Module(body=[], type_ignores=[])
    module.body.append(ast.parse("import logging"))
    module.body.append(ast.parse("import json"))
    module.body.append(ast.parse("logger = logging.getLogger('adli')"))
    return module

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
        Returns exception handler object for given logtypeid.
    '''
    return ast.parse(f"aspAdliLog({name}, {varId})")

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
       Returns a funtion used to log values based on their type as an AST node
       containing the aspAdliLog function definition.
       
       The aspAdliLog function logs values with special handling for objects:
       - For objects with __dict__, it logs their dictionary representation
       - For other values, it logs their string representation
       
       Returns:
          ast.Module: AST node containing the aspAdliLog function definition
    '''

    return ast.parse(
    '''def aspAdliLog(val, varid):
        try:
            val = json.dumps(val, default=lambda o: o.__dict__ )
        except:
            pass
        logger.info(f"# {varid} {val}")
    '''
    )

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
    
    return ast.Module(body=[
        getRootLoggingSetup(fileName).body,
        getLoggingFunction().body,
        getLoggingStatement(json.dumps(header)),
        mainTry
    ], type_ignores=[])

def injectLoggingSetup(tree):
    '''
        Injects logging setup and function into the provided tree.
    '''
    loggingSetup = getLoggingSetup()
    loggingFunction = getLoggingFunction()
    return ast.Module( body=[
        loggingSetup.body,
        loggingFunction.body,
        tree.body
    ], type_ignores=[])


def getAssignStmt(name, value):
    return ast.fix_missing_locations(ast.Assign(
        targets=[ast.Name(id=name, ctx=ast.Store)],
        value=value
    ))