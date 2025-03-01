import ast

class LogInjector(ast.NodeTransformer):
    def __init__(self, node, ltMap, logTypeCount):
        self.ltMap = ltMap
        self.logTypeCount = logTypeCount
        self.funcId = 0
        self.minLogTypeCount = self.logTypeCount
        self.generic_visit(node)
        self.maxLogTypeCount = self.logTypeCount

    def getLogTypeInfo(self, node, type):
        self.logTypeCount += 1
        self.ltMap[self.logTypeCount] = {
            "id": self.logTypeCount,
            "funcid": self.funcId,
            "lineno": node.lineno,
            "end_lineno": node.end_lineno,
            "type": type,
        }
        return ast.parse(f"logger.info({self.logTypeCount})")
    
    def visit_FunctionDef(self, node):
        logStmt = self.getLogTypeInfo(node, "function")
        node.body.insert(0, logStmt)

        self.funcId = self.logTypeCount
        self.generic_visit(node)
        self.funcId = 0
        
        return node

    def visit_Assign(self, node):
        logStmt = self.getLogTypeInfo(node, "child")
        return [logStmt, node]