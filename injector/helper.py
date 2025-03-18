import ast
import os
import copy
import json
import re

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
    return ast.Expr(
        value=ast.Call(
            func=ast.Name(id='aspAdliLog', ctx=ast.Load()),
            args=[
                ast.Name(id=name, ctx=ast.Load()),
                ast.Constant(value=varId)
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
    ).body

def getTraceLoggingFunction():
    ''' 
       Returns a funtion used to log trace start and end locations

       Ex:
       logger.info("@ start <var_value>")
       runJob(jobInfo)
       logger.info("@ end <var_value>")
    '''
    return ast.parse(
    '''def aspTraceLog(traceType, value):
        try:
            value = json.dumps(value, default=lambda o: o.__dict__ )
        except:
            pass
        logger.info(f"@ {traceType} {value}")
    '''
    ).body

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
    traceLoggingFunction = getTraceLoggingFunction()
    header = getLoggingStatement(json.dumps(header))

    mod = ast.Module(body=[], type_ignores=[])
    mod.body = rootLoggingSetup + loggingFunction + traceLoggingFunction + [header] + [mainTry]
    return mod

def injectLoggingSetup(tree):
    '''
        Injects logging setup and function into the provided tree.
    '''
    loggingSetup = getLoggingSetup()
    loggingFunction = getLoggingFunction()
    traceLoggingFunction = getTraceLoggingFunction()
    mod = ast.Module(body=[], type_ignores=[])
    mod.body = loggingSetup + loggingFunction + traceLoggingFunction + tree.body
    return mod

def getDisabledVariables(node):
    """
        This function parses the variable disable comments and returns
        a list with the disabled variables. 

        It parses triple quote comments. 
        Example:
        '''adli-disable-variable value variables'''
    """
    
    disabledVariables = []
    if "value" in node._fields and isinstance(node.value, ast.Constant):

        value = node.value.value
        variables = re.findall("adli-disable-variable (.*)", value)

        if len(variables) > 0:
            disabledVariables = variables[0].split()
        
    return disabledVariables

def getTraceId(node):
    """
        This function parses the asp-adli-trace-id to extract
        the variable which should be logged to indicate the 
        start and end of a unique trace.

        It parses triple quote comments. 
        Example:
        '''adli-trace-id-start <variable_name>'''
        '''adli-trace-id-end <variable_name>'''
    """
    traceVariable = None
    if "value" in node._fields and isinstance(node.value, ast.Constant):
        value = node.value.value
        
        variables = re.findall("adli-trace-id-start (.*)", value)
        if len(variables) > 0:
            return {
                "type": "start",
                "variable": variables[0]
            }
        
        variables = re.findall("adli-trace-id-end (.*)", value)
        if len(variables) > 0:
            return {
                "type": "end",
                "variable": variables[0]
            }
        
    return traceVariable