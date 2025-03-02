import ast
from injector.CollectVariableInfo import CollectAssignVarInfo, CollectFunctionArgInfo
from injector.helper import getVarLogStmt, getLtLogStmt, getAssignStmt

class LogInjector(ast.NodeTransformer):
    def __init__(self, node, ltMap, varMap, logTypeCount):
        self.ltMap = ltMap
        self.varMap = varMap
        self.logTypeCount = logTypeCount
        self.funcId = 0
        self.minLogTypeCount = self.logTypeCount
        self.generic_visit(node)
        self.maxLogTypeCount = self.logTypeCount

    def getLogStmt(self, node, type):
        '''
            This function adds the node to the logtype map and 
            it returns a logging statement to inject.
        '''
        self.logTypeCount += 1
        self.ltMap[self.logTypeCount] = {
            "id": self.logTypeCount,
            "funcid": self.funcId,
            "lineno": node.lineno,
            "end_lineno": node.end_lineno,
            "type": type,
        }
        return getLtLogStmt(self.logTypeCount)
    
    def generateStmts(self, varInfo):
        '''
            This function generates logging statements for all the variables.
            An assign statement is created for temporary variables before logging
            their value. Temporary variables are saved in preLog and the target
            variable is saved in post log.
        '''
        preLog = []
        postLog = []  
        for variable in varInfo:
            if variable["assignValue"] is None:
                postLog.append(getVarLogStmt(variable["name"], variable["varId"]))
            else:
                preLog.append(getAssignStmt(variable["name"], variable["assignValue"]))
                preLog.append(getVarLogStmt(variable["name"], variable["varId"]))
            del variable["assignValue"]
            self.varMap[variable["varId"]] = variable

        return preLog, postLog
    
    def visit_FunctionDef(self, node):
        '''
            This function adds a log statement to function body.
            It sets a function id before visiting child nodes and
            resets it back to global scope(0).
        '''
        logStmt = self.getLogStmt(node, "function")

        # Add log statements for arguments. This will be obsolete once support
        # is added for extracting arguments from the place func was called.
        variables = CollectFunctionArgInfo(node).variables
        preLog, postLog = self.generateStmts(variables)
        if len(preLog) > 0:
            node.body.insert(0, preLog)
        node.body.insert(0, logStmt)

        self.funcId = self.logTypeCount
        self.generic_visit(node)
        self.funcId = 0
        
        return node

    def visit_Assign(self, node):
        '''
            Visit assign statement and extract variables.
        '''
        logStmt = self.getLogStmt(node, "child")

        allPreLogs = []
        allPostLogs = []
        for target in node.targets:
            varInfo = CollectAssignVarInfo(target).variables
            preLog, postLog = self.generateStmts(varInfo)
            allPreLogs.extend(preLog)
            allPostLogs.extend(postLog)

        return allPreLogs + [logStmt]+ [node] + allPostLogs
    
    def visit_AugAssign(self, node):
        '''
            Visit AugAssign statement and extract variables.
        '''
        logStmt = self.getLogStmt(node, "child")
        varInfo = CollectAssignVarInfo(node.target).variables
        preLog, postLog = self.generateStmts(varInfo)

        return preLog + [logStmt]+ [node] + postLog
    
    def visit_AnnAssign(self, node):
        '''
            Visit AnnAssign statement and extract variables if it has a value.
        '''
        logStmt = self.getLogStmt(node, "child")

        if node.value:
            varInfo = CollectAssignVarInfo(node.target).variables
            preLog, postLog = self.generateStmts(varInfo)
            return preLog + [logStmt]+ [node] + postLog
        else:
            return [logStmt, node]