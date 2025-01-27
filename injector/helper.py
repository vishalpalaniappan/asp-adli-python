import ast, os

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
        module = os.path.join(
            rootDir,
            node.module.replace('.','/')
        )
        name = os.path.join(
            node.names[0].name.replace('.','/')
        )
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
    module.body.append(ast.parse("import sys"))
    module.body.append(ast.parse("from pathlib import Path"))
    module.body.append(ast.parse("from clp_logging.handlers import CLPFileHandler"))
    s = "clp_handler = CLPFileHandler(Path('{f}'))".format(f='./' + logFileName + '.cdl')
    module.body.append(ast.parse(s))
    module.body.append(ast.parse("logger = logging.getLogger('root')"))
    module.body.append(ast.parse("logger.setLevel(logging.INFO)"))
    module.body.append(ast.parse("logger.addHandler(clp_handler)"))
    return module

def getLoggingSetup():
    """
        Returns the logging setup for any imported files.
    """
    module = ast.Module(body=[], type_ignores=[])
    module.body.append(ast.parse("import logging"))
    module.body.append(ast.parse("logger = logging.getLogger('root')"))
    return module

def getLoggingStatement(syntax):
    """
        Returns a logging statement as an AST node.
    """
    return ast.Expr(
        ast.Call(
            func=ast.Name(id='logger.info', ctx=ast.Load()),
            args=[ast.Constant(value=syntax)],
            keywords=[]
        )
    )

def getExceptionLog():
    '''
        Returns exception handler object for given logtypeid.
    '''
    return ast.ExceptHandler(
        type=ast.Name(id='Exception', ctx=ast.Load()),
        name='e',
        body=[
            ast.parse("logger.error(f\"? {traceback.format_exc()}\")"),
            ast.parse("raise"),
        ]
    )

def getLoggingFunction():
    ''' 
       Returns a funtion used to log values based on their type.
       Returns an AST node containing the aspAdliLog function definition.
       
       The aspAdliLog function logs values with special handling for objects:
       - For objects with __dict__, it logs their dictionary representation
       - For other values, it logs their string representation
       
       Returns:
          ast.Module: AST node containing the aspAdliLog function definition
    '''

    return ast.parse(
    '''def aspAdliLog(val, logtypeid):
    if hasattr(val, "__dict__"):
        val = val.__dict__
    logger.info(f"# {logtypeid} {val}")
    '''
    )