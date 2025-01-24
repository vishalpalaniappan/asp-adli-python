import ast

def checkImport(filePath, node):
    """
        Given an import statement, this function tests if
        it is a local import and returns the path.
    """
    pathsToCheck = []
    if isinstance(node, ast.Import):
        name = node.names[0].name.replace('.','/')
        path = name + '.py'
        pathsToCheck.append(path)
    elif isinstance(node, ast.ImportFrom):
        module = node.module.replace('.','/')
        name = node.names[0].name.replace('.','/')
        pathsToCheck.append(f"{module}/{name}.py".format(module,name))
        pathsToCheck.append(f"{module}.py".format(module))
    
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
    module.body.append(ast.parse("import logging"))
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

def getExceptionLog(logtype_id):
    '''
        Returns exception handler object for given logtypeid.
    '''
    return ast.ExceptHandler(
        type=ast.Name(id='Exception', ctx=ast.Load()),
        name='e',
        body=[
            ast.parse("logger.info(f\"? " + str(logtype_id) +" {str(e)}\")"),
            ast.parse("raise e")
        ]
    )