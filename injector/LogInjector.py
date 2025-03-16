import ast
from injector.helper import getVarLogStmt, getLtLogStmt, getAssignStmt, getDisabledVariables
from injector.CollectVariables import CollectVariables

class LogInjector(ast.NodeTransformer):
    def __init__(self, node, ltMap, logTypeCount):
        self.ltMap = ltMap
        self.varMap = {}
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
        if not hasattr(node, 'lineno') or not hasattr(node, 'end_lineno'):
            raise ValueError(f"AST node of type {type(node).__name__} missing required line number information")

        self.logTypeCount += 1

        self.ltMap[self.logTypeCount] = {
            "id": self.logTypeCount,
            "funcid": self.funcId,
            "lineno": node.lineno,
            "end_lineno": node.end_lineno,
            "type": type,
        }

        return getLtLogStmt(self.logTypeCount)
    
    def generateVarLogStmts(self, node):
        '''
            This function generates logging statements for all the variables.
            An assign statement is created for temporary variables before logging
            their value. Temporary variables are saved in preLog and the target
            variable is saved in post log.
        '''
        varInfo = CollectVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
        logs = []
        for variable in varInfo:
            variable["global"] = variable["name"] in self.globalsInFunc or variable["funcId"] == 0

            if variable["global"] and variable["name"] in self.globalDisabledVariables:
                continue 

            if not variable["global"] and variable["name"] in self.disabledVariables:
                continue 

            logs.append(getVarLogStmt(variable["name"], variable["varId"]))

            self.varMap[variable["varId"]] = variable

        return logs
    
    def visit_FunctionDef(self, node):
        '''
            This function adds a log statement to function body.
            It sets a function id before visiting child nodes and
            resets it back to global scope(0).
        '''
        logStmt = self.generateLtLogStmts(node, "function")

        self.funcId = self.logTypeCount
        self.ltMap[self.logTypeCount]["funcid"] = self.logTypeCount
        self.ltMap[self.logTypeCount]["name"] = node.name

        # Reset function specific variables before visiting children.
        self.disabledVariables = []
        self.globalsInFunc = []

        varLogStmt = self.generateVarLogStmts(node)
        self.generic_visit(node)

        node.body = [logStmt] + varLogStmt + node.body
        
        self.funcId = 0
        
        return node
    
    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    def visit_Assign(self, node):
        '''
            Visit assign statement and extract variables from the target nodes.
        '''
        logStmt = self.generateLtLogStmts(node, "child")
        varLogStmt = self.generateVarLogStmts(node)

        return [logStmt]+ [node] + varLogStmt
    
    def visit_AugAssign(self, node):
        '''
            Visit AugAssign statement and extract variables from the target node.
        '''
        logStmt = self.generateLtLogStmts(node, "child")
        varLogStmt = self.generateVarLogStmts(node)

        return [logStmt]+ [node] + varLogStmt
    
    def visit_AnnAssign(self, node):
        '''
            Visit AnnAssign statement and extract variables from target node
            if it has a value.
        '''
        logStmt = self.generateLtLogStmts(node, "child")

        if node.value:
            varLogStmt = self.generateVarLogStmts(node)
            return [logStmt]+ [node] + varLogStmt
        else:
            return [logStmt, node]
    '''
        INJECT LOGS TYPE A
        Example:
            logger.info(<logtype_id>)
            <original_ast_node>
            logger.info(<var_id_1>)
            ...
            logger.info(<var_id_n>)
    '''
    def injectLogTypesA(self, node):
        logStmt = self.generateLtLogStmts(node, "child")
        self.generic_visit(node)
        varLogStmt = self.generateVarLogStmts(node)
        return [logStmt] + [node] + varLogStmt
    
    def visit_Global(self, node):
        self.globalsInFunc += node.names
        return self.injectLogTypesA(node)

    def visit_Expr(self, node):
        if (self.funcId == 0):
            self.globalDisabledVariables += getDisabledVariables(node)
        else:
            self.disabledVariables += getDisabledVariables(node)
        return self.injectLogTypesA(node)

    def visit_Pass(self, node):
        return self.injectLogTypesA(node)
    
    def visit_Delete(self, node):
        return self.injectLogTypesA(node)
    
    def visit_Nonlocal(self, node):
        return self.injectLogTypesA(node)
    
    def visit_Break(self, node):
        return self.injectLogTypesA(node)
    
    def visit_Continue(self, node):
        return self.injectLogTypesA(node)
    
    def visit_Assert(self, node):
        return self.injectLogTypesA(node)
    
    def visit_Raise(self, node):
        return self.injectLogTypesA(node)
    
    def visit_Return(self, node):
        return self.injectLogTypesA(node)

    def visit_Import(self, node):
        return self.injectLogTypesA(node)
    
    def visit_ImportFrom(self, node):
        return self.injectLogTypesA(node)    

    '''
        INJECT LOGS TYPE B
        Example:
            logger.info(<logtype_id>)
            if <expression>:
                logger.info(<var_id_1>)
                ...
                logger.info(<var_id_n>)
    '''
    def injectLogTypesB(self, node):
        logStmt = self.generateLtLogStmts(node, "child")
        self.generic_visit(node)
        varLogStmt = self.generateVarLogStmts(node)
        node.body = varLogStmt + node.body
        return [logStmt, node]

    def visit_With(self, node):
        return self.injectLogTypesB(node)
    
    def visit_If(self, node):
        return self.injectLogTypesB(node)
    
    def visit_AsyncWith(self, node):
        return self.injectLogTypesB(node)
    

    '''
        INJECT LOGS TYPE C
        Example
            def func_1():
                logger.info(<logtype_id>)
                ...
                logger.info(<var_id_1>)
                logger.info(<var_id_n>):
    '''
    def injectLogTypesC(self, node):
        logStmt = self.generateLtLogStmts(node, "child")
        self.generic_visit(node)
        varLogStmt = self.generateVarLogStmts(node)
        node.body = [logStmt] + varLogStmt + node.body
        return [node]

    def visit_ClassDef(self, node):
        return self.injectLogTypesC(node)
    
    def visit_Try(self, node):
        return self.injectLogTypesC(node)

    def visit_TryFinally(self, node):
        return self.injectLogTypesC(node)

    def visit_TryExcept(self, node):
        return self.injectLogTypesC(node)

    def visit_ExceptHandler(self, node):
        return self.injectLogTypesC(node)
    
    '''
        INJECT LOGS TYPE D
        Example:
            logger.info(<logtype_id>)
            for <expression>:
                logger.info(<var_id_1>)
                logger.info(<var_id_n>)
                ...
                logger.info(<logtype_id>)
    '''    
    def injectLogTypesD(self, node):
        logStmt = self.generateLtLogStmts(node, "child")
        self.generic_visit(node)
        varLogStmt = self.generateVarLogStmts(node)
        node.body = varLogStmt + node.body + [logStmt]
        return [logStmt, node]
    
    def visit_For(self, node):
        return self.injectLogTypesD(node)
    
    def visit_AsyncFor(self, node):
        return self.injectLogTypesD(node)
    
    def visit_While(self, node):
        return self.injectLogTypesD(node)



