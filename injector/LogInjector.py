import ast
from injector.CollectVariableInfo import CollectAssignVarInfo, CollectFunctionArgInfo
from injector.helper import getVarLogStmt, getLtLogStmt, getAssignStmt, getDisabledVariables

class LogInjector(ast.NodeTransformer):
    def __init__(self, node, ltMap, varMap, logTypeCount):
        self.ltMap = ltMap
        self.varMap = varMap
        self.logTypeCount = logTypeCount
        self.funcId = 0

        self.globalsInFunc = []
        self.globalDisabledVariables = []
        self.disabledVariables = []

        self.minLogTypeCount = self.logTypeCount
        self.generic_visit(node)
        self.maxLogTypeCount = self.logTypeCount

    def generateLtLogStmts(self, node, type):
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
    
    def generateVarLogStmts(self, varInfo):
        '''
            This function generates logging statements for all the variables.
            An assign statement is created for temporary variables before logging
            their value. Temporary variables are saved in preLog and the target
            variable is saved in post log.
        '''
        preLog = []
        postLog = []  
        for variable in varInfo:
            variable["global"] = variable["name"] in self.globalsInFunc

            if variable["global"] == True and variable["name"] in self.globalDisabledVariables:
                continue 

            if variable["global"] == False and variable["name"] in self.disabledVariables:
                continue 

            if variable["assignValue"] is None:
                postLog.append(getVarLogStmt(variable["syntax"], variable["varId"]))
            else:                
                preLog.append(getAssignStmt(variable["name"], variable["assignValue"]))
                preLog.append(getVarLogStmt(variable["syntax"], variable["varId"]))

            del variable["assignValue"]
            del variable["syntax"]
            self.varMap[variable["varId"]] = variable

        return preLog, postLog
    
    def visit_FunctionDef(self, node):
        '''
            This function adds a log statement to function body.
            It sets a function id before visiting child nodes and
            resets it back to global scope(0).
        '''
        logStmt = self.generateLtLogStmts(node, "function")

        self.funcId = self.logTypeCount
        self.globalsInFunc = []

        # Add log statements for arguments. This is temporary and will be replced.
        variables = CollectFunctionArgInfo(node, self.logTypeCount, self.funcId).variables
        preLog, postLog = self.generateVarLogStmts(variables)
        node.body = [logStmt] + postLog + node.body

        self.generic_visit(node)
        self.funcId = 0
        
        return node
    
    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    def visit_Assign(self, node):
        '''
            Visit assign statement and extract variables.
        '''
        logStmt = self.generateLtLogStmts(node, "child")

        allPreLogs = []
        allPostLogs = []
        for target in node.targets:
            varInfo = CollectAssignVarInfo(target, self.logTypeCount, self.funcId).variables
            preLog, postLog = self.generateVarLogStmts(varInfo)
            allPreLogs.extend(preLog)
            allPostLogs.extend(postLog)

        return allPreLogs + [logStmt]+ [node] + allPostLogs
    
    def visit_AugAssign(self, node):
        '''
            Visit AugAssign statement and extract variables.
        '''
        logStmt = self.generateLtLogStmts(node, "child")

        varInfo = CollectAssignVarInfo(node.target, self.logTypeCount, self.funcId).variables
        preLog, postLog = self.generateVarLogStmts(varInfo)

        return preLog + [logStmt]+ [node] + postLog
    
    def visit_AnnAssign(self, node):
        '''
            Visit AnnAssign statement and extract variables if it has a value.
        '''
        logStmt = self.generateLtLogStmts(node, "child")

        if node.value:
            varInfo = CollectAssignVarInfo(node.target, self.logTypeCount, self.funcId).variables
            preLog, postLog = self.generateVarLogStmts(varInfo)
            return preLog + [logStmt]+ [node] + postLog
        else:
            return [logStmt, node]

    def visit_Global(self, node):
        '''
            Visit global statement and save global variables.
        '''
        self.globalsInFunc += node.names
        logStmt = self.generateLtLogStmts(node, "child")
        return [logStmt, node]

    def visit_Expr(self, node):
        '''
            Visit expression statement and check for disabled variables.
        '''
        if (self.funcId == 0):
            self.globalDisabledVariables += getDisabledVariables(node)
        else:
            self.disabledVariables += getDisabledVariables(node)
        return node
