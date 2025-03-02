import ast
from injector.CollectVariableInfo import CollectVariableInfo
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
        preLog = []
        postLog = []  
        for variable in varInfo:
            if variable["node"] is None:
                postLog.append(getVarLogStmt(variable["name"], variable["varId"]))
            else:
                preLog.append(getAssignStmt(variable["name"], variable["node"]))
                preLog.append(getVarLogStmt(variable["name"], variable["varId"]))
            del variable["node"]
            self.varMap[variable["varId"]] = variable

        return preLog, postLog
    
    def visit_FunctionDef(self, node):
        '''
            This function adds a log statement to function body.
            It sets a function id before visiting child nodes and
            resets it back to global scope(0).
        '''
        logStmt = self.getLogStmt(node, "function")
        node.body.insert(0, logStmt)

        self.funcId = self.logTypeCount
        self.generic_visit(node)
        self.funcId = 0
        
        return node

    def visit_Assign(self, node):
        '''
            Visit assign statement.
        '''
        logStmt = self.getLogStmt(node, "child")

        allPreLogs = []
        allPostLogs = []
        for target in node.targets:
            varInfo = CollectVariableInfo(target).variables
            preLog, postLog = self.generateStmts(varInfo)
            allPreLogs.extend(preLog)
            allPostLogs.extend(postLog)

        updatedNodes = []
        updatedNodes.extend(allPreLogs)
        updatedNodes.append(logStmt)
        updatedNodes.append(node)
        updatedNodes.extend(allPostLogs)

        return updatedNodes