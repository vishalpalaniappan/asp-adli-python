import ast
from injector.CollectVariableInfo import CollectVariableInfo

class LogInjector(ast.NodeTransformer):
    def __init__(self, node, ltMap, logTypeCount):
        self.ltMap = ltMap
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
        return ast.parse(f"logger.info({self.logTypeCount})").body[0]
    
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

        for target in node.targets:
            CollectVariableInfo(target).getVariableInfo()
        return [logStmt, node]