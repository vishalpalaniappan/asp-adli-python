import ast
from injector.helper import getVarLogStmt, getLtLogStmt, getAssignStmt
from injector.VariableCollectors.CollectAssignVarInfo import CollectAssignVarInfo
from injector.VariableCollectors.CollectVariableDefault import CollectVariableDefault
from injector.VariableCollectors.CollectCallVariables import CollectCallVariables
from injector.VariableCollectors.CollectFunctionArgInfo import CollectFunctionArgInfo

from injector.CommentCollectors.getDisabledVariable import getDisabledVariables
from injector.CommentCollectors.getMetadata import getMetadata

class LogInjector(ast.NodeTransformer):
    def __init__(self, node, ltMap, logTypeCount):
        self.metadata = None
        self.ltMap = ltMap
        self.varMap = {}
        self.logTypeCount = logTypeCount
        self.funcId = 0

        self.globalsInFunc = []
        self.globalDisabledVariables = []
        self.localDisabledVariables = []
        self.nodeVarInfo = []

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
            "isUnique": False
        }

        return getLtLogStmt(self.logTypeCount)
    
    def generateVarLogStmts(self):
        '''
            This function generates logging statements for all the variables.
            An assign statement is created for temporary variables before logging
            their value. Temporary variables are saved in preLog and the target
            variable is saved in post log.
        '''
        preLog = []
        postLog = []  
        for variable in self.nodeVarInfo:
            variable["global"] = variable["name"] in self.globalsInFunc or variable["funcId"] == 0

            if variable["global"] and variable["name"] in self.globalDisabledVariables:
                continue 

            if not variable["global"] and variable["name"] in self.localDisabledVariables:
                continue 

            if variable["assignValue"] is None:
                postLog.append(getVarLogStmt(variable["syntax"], variable["varId"]))
            else:                
                preLog.append(getAssignStmt(variable["name"], variable["assignValue"]))
                preLog.append(getVarLogStmt(variable["syntax"], variable["varId"]))

            ''' 
            Variables named "asp_uid" mark a function as the start of a unique trace.
            It is a reserved adli keyword and coming updates will ensure that it is only
            written to once in a function and will raise an error if this is violated.
            '''
            if variable["name"] == "asp_uid":
                self.ltMap[variable["funcId"]]["isUnique"] = True

            del variable["assignValue"]
            del variable["syntax"]
            self.varMap[variable["varId"]] = variable

        self.nodeVarInfo= []
        return preLog, postLog
    
    def visit_FunctionDef(self, node):
        '''
            This function adds a log statement to function body.
            It sets a function id before visiting child nodes and
            resets it back to global scope(0).
        '''
        logStmt = self.generateLtLogStmts(node, "function")

        self.funcId = self.logTypeCount

        # Update the log type map to add function specific information
        self.ltMap[self.logTypeCount]["funcid"] = self.logTypeCount
        self.ltMap[self.logTypeCount]["name"] = node.name

        # Reset function specific variables before visiting children.
        self.localDisabledVariables = []
        self.globalsInFunc = []

        self.generic_visit(node)

        # Add log statements for arguments. This is temporary and will be replaced.
        self.nodeVarInfo += CollectFunctionArgInfo(node, self.logTypeCount, self.funcId).variables
        self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
        preLog, postLog = self.generateVarLogStmts()
        node.body = [logStmt] + postLog + node.body
        
        self.funcId = 0
        
        return preLog + [node]
    
    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    def visit_Assign(self, node):
        '''
            Visit assign statement and extract variables from the target nodes.
        '''
        logStmt = self.generateLtLogStmts(node, "child")

        for target in node.targets:
            self.nodeVarInfo += CollectAssignVarInfo(target, self.logTypeCount, self.funcId).variables
        
        self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
            
        preLog, postLog = self.generateVarLogStmts()

        return preLog + [logStmt]+ [node] + postLog
    
    def visit_AugAssign(self, node):
        '''
            Visit AugAssign statement and extract variables from the target node.
        '''
        logStmt = self.generateLtLogStmts(node, "child")

        self.nodeVarInfo += CollectAssignVarInfo(node.target, self.logTypeCount, self.funcId).variables
        self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
        preLog, postLog = self.generateVarLogStmts()

        return preLog + [logStmt]+ [node] + postLog
    
    def visit_AnnAssign(self, node):
        '''
            Visit AnnAssign statement and extract variables from target node
            if it has a value.
        '''
        logStmt = self.generateLtLogStmts(node, "child")

        if node.value:
            self.nodeVarInfo += CollectAssignVarInfo(node.target, self.logTypeCount, self.funcId).variables
            self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
            preLog, postLog = self.generateVarLogStmts()
            return preLog + [logStmt]+ [node] + postLog
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
        self.nodeVarInfo += CollectVariableDefault(node, self.logTypeCount, self.funcId).variables
        self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
        preLog, postLog = self.generateVarLogStmts()
        return preLog + [logStmt] + [node] + postLog
    
    def visit_Global(self, node):
        self.globalsInFunc += node.names
        return self.injectLogTypesA(node)

    def visit_Expr(self, node):
        # Save disabled variables.
        if (self.funcId == 0):
            self.globalDisabledVariables += getDisabledVariables(node)
        else:
            self.localDisabledVariables += getDisabledVariables(node)

        # Save the metadata
        obj = getMetadata(node)
        if (obj and obj["type"] == "adli_metadata"):
            self.metadata = obj

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
        self.nodeVarInfo += CollectVariableDefault(node, self.logTypeCount, self.funcId).variables
        self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
        preLog, postLog = self.generateVarLogStmts()
        node.body = postLog + node.body
        return preLog + [logStmt, node]

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
        self.nodeVarInfo += CollectVariableDefault(node, self.logTypeCount, self.funcId).variables
        self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
        preLog, postLog = self.generateVarLogStmts()
        node.body = [logStmt] + postLog + node.body
        return preLog + [node]

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
        self.nodeVarInfo += CollectVariableDefault(node, self.logTypeCount, self.funcId).variables
        self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
        preLog, postLog = self.generateVarLogStmts()
        node.body = postLog + node.body + [logStmt]
        return preLog + [logStmt, node]
    
    def visit_For(self, node):
        return self.injectLogTypesD(node)
    
    def visit_AsyncFor(self, node):
        return self.injectLogTypesD(node)
    
    def visit_While(self, node):
        return self.injectLogTypesD(node)



