import ast
import json
from injector.helper import getVarLogStmt, getLtLogStmt, getAssignStmt, getAdliConfiguration, getEncodedOutputStmt, getEmptyRootNode, getUniqueIdAssignStmt, getRootUidAssign
from injector.helper import injectRootLoggingSetup, injectLoggingSetup, getTag
from injector.VariableCollectors.CollectAssignVarInfo import CollectAssignVarInfo
from injector.VariableCollectors.CollectVariableDefault import CollectVariableDefault
from injector.VariableCollectors.CollectCallVariables import CollectCallVariables
from injector.VariableCollectors.CollectFunctionArgInfo import CollectFunctionArgInfo

class LogInjector(ast.NodeTransformer):
    def __init__(self, tree, logTypeCount, file, isRoot):
        self.metadata = None
        self.ltMap = {}
        self.varMap = {}
        self.logTypeCount = logTypeCount
        self.funcId = 0
        self.file = file

        self.globalsInFunc = []
        self.globalDisabledVariables = []
        self.localDisabledVariables = []
        self.nodeVarInfo = []

        self.minLogTypeCount = self.logTypeCount
        self.generic_visit(tree)
        tree.body.insert(0, getRootUidAssign())
        self.maxLogTypeCount = self.logTypeCount

        self.tree = injectRootLoggingSetup(tree) if isRoot else injectLoggingSetup(tree)

        self.updateLineNumbers()

    def updateLineNumbers(self):
        '''
            Save the line number of the log type in the injected source.
        '''
        # Reparse the tree to update the line numbers
        parsed = ast.unparse(self.tree)
        tree = ast.parse(parsed)
        
        # Walk the tree and find the tagged notes to update the line number
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                try:
                    val = json.loads(node.value.value)

                    if val["type"] == "adli_tag":
                        ltInfo = self.ltMap[val["lt"]]
                        if val["dir"] == "prev":
                            newLineno = node.lineno - 1
                        elif val["dir"] == "next":    
                            newLineno = node.lineno + 1

                        ltInfo["injectedLineno"] = newLineno
                except:
                    pass               


    def generateLtLogStmts(self, node, type):
        '''
            This function adds the node to the logtype map and 
            it returns a logging statement to inject.
        '''
        if not hasattr(node, 'lineno') or not hasattr(node, 'end_lineno'):
            raise ValueError(f"AST node of type {type(node).__name__} missing required line number information")

        self.logTypeCount += 1

        # Save the logtype count in the node. This is used to save the new lineno in ltMap after injecting the logs.
        node.logTypeCount = self.logTypeCount

        self.ltMap[self.logTypeCount] = {
            "id": self.logTypeCount,
            "file": self.file,
            "funcid": self.funcId,
            "lineno": node.lineno,
            "end_lineno": node.end_lineno,
            "type": type,
            "statement": ast.unparse(getEmptyRootNode(node) if "body" in node._fields else node)
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

    def processFunctionNode(self, node, isAsync):
        '''
            This function adds a log statement to function body.
            It sets a function id before visiting child nodes and
            resets it back to global scope(0).
        '''
        logStmt = self.generateLtLogStmts(node, "function")
        meta_tag = getTag(self.logTypeCount, "prev")

        self.funcId = self.logTypeCount

        # Update the log type map to add function specific information
        self.ltMap[self.logTypeCount]["funcid"] = self.logTypeCount
        self.ltMap[self.logTypeCount]["name"] = node.name
        self.ltMap[self.logTypeCount]["isAsync"] = isAsync

        # Reset function specific variables before visiting children.
        self.localDisabledVariables = []
        self.globalsInFunc = []

        self.generic_visit(node)

        # Add log statements for arguments. This is temporary and will be replaced.
        self.nodeVarInfo += CollectFunctionArgInfo(node, self.logTypeCount, self.funcId).variables
        self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
        preLog, postLog = self.generateVarLogStmts()

        uidAssign = getUniqueIdAssignStmt()
        node.body = [meta_tag, uidAssign, logStmt] + postLog + node.body
        
        self.funcId = 0
        
        return preLog + [node]

    
    def visit_FunctionDef(self, node):
        return self.processFunctionNode(node, isAsync= False)  
      
    def visit_AsyncFunctionDef(self, node):
        return self.processFunctionNode(node, isAsync= True)

    def visit_Assign(self, node):
        '''
            Visit assign statement and extract variables from the target nodes.
        '''
        logStmt = self.generateLtLogStmts(node, "child")
        meta_tag = getTag(self.logTypeCount, "next")

        for target in node.targets:
            self.nodeVarInfo += CollectAssignVarInfo(target, self.logTypeCount, self.funcId).variables
        
        self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
            
        preLog, postLog = self.generateVarLogStmts()

        return preLog + [logStmt, meta_tag, node] + postLog
    
    def visit_AugAssign(self, node):
        '''
            Visit AugAssign statement and extract variables from the target node.
        '''
        logStmt = self.generateLtLogStmts(node, "child")
        meta_tag = getTag(self.logTypeCount, "next")

        self.nodeVarInfo += CollectAssignVarInfo(node.target, self.logTypeCount, self.funcId).variables
        self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
        preLog, postLog = self.generateVarLogStmts()

        return preLog + [logStmt, meta_tag, node] + postLog
    
    def visit_AnnAssign(self, node):
        '''
            Visit AnnAssign statement and extract variables from target node
            if it has a value.
        '''
        logStmt = self.generateLtLogStmts(node, "child")
        meta_tag = getTag(self.logTypeCount, "next")

        if node.value:
            self.nodeVarInfo += CollectAssignVarInfo(node.target, self.logTypeCount, self.funcId).variables
            self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
            preLog, postLog = self.generateVarLogStmts()
            return preLog + [logStmt, meta_tag, node] + postLog
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
        meta_tag = getTag(self.logTypeCount, "next")
        self.generic_visit(node)
        self.nodeVarInfo += CollectVariableDefault(node, self.logTypeCount, self.funcId).variables
        self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
        preLog, postLog = self.generateVarLogStmts()
        return preLog + [logStmt, meta_tag, node] + postLog
    
    def visit_Global(self, node):
        self.globalsInFunc += node.names
        return self.injectLogTypesA(node)

    def visit_Expr(self, node):
        parsed = getAdliConfiguration(node)

        if (parsed and parsed["type"] == "adli_disable_variable"):
            # TODO: Add validation for the values.
            if (self.funcId == 0):
                self.globalDisabledVariables += parsed["value"]
            else:
                self.localDisabledVariables += parsed["value"]
        elif (parsed and parsed["type"] == "adli_metadata"):
            self.metadata = parsed["value"]
        elif (parsed and parsed["type"] == "adli_encode_output"):
            encodedStmt = getEncodedOutputStmt(parsed["value"][0])
            return encodedStmt

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
        meta_tag = getTag(self.logTypeCount, "next")
        self.generic_visit(node)
        self.nodeVarInfo += CollectVariableDefault(node, self.logTypeCount, self.funcId).variables
        self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
        preLog, postLog = self.generateVarLogStmts()
        node.body = postLog + node.body
        return preLog + [logStmt, meta_tag, node]

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
        meta_tag = getTag(self.logTypeCount, "prev")
        self.generic_visit(node)
        self.nodeVarInfo += CollectVariableDefault(node, self.logTypeCount, self.funcId).variables
        self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
        preLog, postLog = self.generateVarLogStmts()
        node.body = [meta_tag, logStmt] + postLog + node.body
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
        meta_tag = getTag(self.logTypeCount, "next")
        self.generic_visit(node)
        self.nodeVarInfo += CollectVariableDefault(node, self.logTypeCount, self.funcId).variables
        self.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables
        preLog, postLog = self.generateVarLogStmts()
        node.body = postLog + node.body + [logStmt]
        return preLog + [logStmt, meta_tag, node]
    
    def visit_For(self, node):
        return self.injectLogTypesD(node)
    
    def visit_AsyncFor(self, node):
        return self.injectLogTypesD(node)
    
    def visit_While(self, node):
        return self.injectLogTypesD(node)



