import ast
import json
from injector.helper import getVarLogStmt, getLtLogStmt, getAssignStmt, getAdliConfiguration, getEncodedOutputStmt, getEmptyRootNode, getUniqueIdAssignStmt, getRootUidAssign
from injector.helper import injectRootLoggingSetup, injectLoggingSetup, getTag
from injector.VariableCollectors.CollectAssignVarInfo import CollectAssignVarInfo
from injector.VariableCollectors.CollectVariableDefault import CollectVariableDefault
from injector.VariableCollectors.CollectCallVariables import CollectCallVariables
from injector.VariableCollectors.CollectFunctionArgInfo import CollectFunctionArgInfo

class LogInjectorDesign(ast.NodeTransformer):
    def __init__(self, source, tree, logTypeCount, file, isRoot, absMap, sdg_meta):
        self.metadata = None
        self.ltMap = {}
        self.varMap = {}
        self.logTypeCount = logTypeCount
        self.funcId = 0
        self.file = file
        self.source = source
        self.sdg_meta = sdg_meta

        if (absMap):
            self.fileAbsMap = absMap[file]
        else:
            self.fileAbsMap = None

        self.nodeVarInfo = []

        self.abstraction_meta_stack = []

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


    def generateLtLogStmts(self, node, isFunc, type):
        '''
            This function adds the node to the logtype map and 
            it returns a logging statement to inject.
        '''
        if not hasattr(node, 'lineno') or not hasattr(node, 'end_lineno'):
            raise ValueError(f"AST node of type {type(node).__name__} missing required line number information")

        self.logTypeCount += 1

        # Save the logtype count in the node. This is used to save the new lineno in ltMap after injecting the logs.
        node.logTypeCount = self.logTypeCount


        absMeta = None
        variables = []

        # Get the abstraction metadata if available.
        if self.fileAbsMap and node.lineno in self.fileAbsMap:
            absMeta = self.fileAbsMap[node.lineno]
            meta = self.sdg_meta["abstractions"][absMeta]
            if "variables" in meta:
                variables = meta["variables"]

        self.ltMap[self.logTypeCount] = {
            "id": self.logTypeCount,
            "file": self.file,
            "funcid": self.funcId,
            "lineno": node.lineno,
            "end_lineno": node.end_lineno,
            "type": type,
            "statement": ast.unparse(getEmptyRootNode(node) if "body" in node._fields else node),
            "abstractionId": absMeta
        }

        if (isFunc):
            funcId = self.logTypeCount
        else:
            funcId = self.funcId

        varLogs = []
        for variable in variables:
            varInfo = {
                "varId": absMeta + "_" + variable["name"],
                "name": variable["name"],
                "keys": [],
                "syntax": variable["name"],
                "meta": meta["intent"],
                "logType": self.logTypeCount,
                "funcId": funcId,
                "isTemp": False,
                "global": False
            }
            varLogs.append(getVarLogStmt(varInfo["syntax"], varInfo["varId"]))
            self.varMap[varInfo["varId"]] = varInfo

        return {
            "logStmt": getLtLogStmt(self.logTypeCount),
            "varLogs": varLogs
        }

    def processFunctionNode(self, node, isAsync):
        '''
            This function adds a log statement to function body.
            It sets a function id before visiting child nodes and
            resets it back to global scope(0).
        '''
        logStmt = self.generateLtLogStmts(node, True, "function")
        meta_tag = getTag(self.logTypeCount, "prev")

        self.funcId = self.logTypeCount

        # Update the log type map to add function specific information
        self.ltMap[self.logTypeCount]["funcid"] = self.logTypeCount
        self.ltMap[self.logTypeCount]["name"] = node.name
        self.ltMap[self.logTypeCount]["isAsync"] = isAsync

        self.generic_visit(node)

        uidAssign = getUniqueIdAssignStmt()
        node.body = [meta_tag, uidAssign] + node.body
        
        self.funcId = 0
        
        return [node]

    
    def visit_FunctionDef(self, node):
        return self.processFunctionNode(node, isAsync= False)  
      
    def visit_AsyncFunctionDef(self, node):
        return self.processFunctionNode(node, isAsync= True)

    def visit_Assign(self, node):
        '''
            Visit assign statement and extract variables from the target nodes.
        '''
        logs = self.generateLtLogStmts(node, False, "child")
        meta_tag = getTag(self.logTypeCount, "next")

        return [logs["logStmt"], meta_tag, node] + logs["varLogs"]
    
    def visit_AugAssign(self, node):
        '''
            Visit AugAssign statement and extract variables from the target node.
        '''
        logs = self.generateLtLogStmts(node, "child")
        meta_tag = getTag(self.logTypeCount, "next")

        if node.value:
            return [logs["logStmt"], meta_tag, node] + logs["varLogs"]
        else:
            return [logs["logStmt"], node]
    
    def visit_AnnAssign(self, node):
        '''
            Visit AnnAssign statement and extract variables from target node
            if it has a value.
        '''
        logs = self.generateLtLogStmts(node, False, "child")
        meta_tag = getTag(self.logTypeCount, "next")
        return [logs["logStmt"], meta_tag, node] + logs["varLogs"]
    
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
        logs = self.generateLtLogStmts(node, False, "child")
        meta_tag = getTag(self.logTypeCount, "next")
        self.generic_visit(node)
        return [logs["logStmt"], meta_tag, node] + logs["varLogs"]

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
        
        # Check if the Expr is a triple quote comment:
        # - If it is, then don't inject logs.
        # - If it isn't, then inject logs.
        '''
            {
                "type":"adli_disable_variable",
                "value":["segment"]
            }
        '''
        segment = ast.get_source_segment(self.source, node)
        isComment = segment and segment.lstrip().startswith(("'''", '"""'))
        
        if isComment:
            return node
        else:
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
        logs = self.generateLtLogStmts(node, False, "child")
        meta_tag = getTag(self.logTypeCount, "next")
        self.generic_visit(node)
        node.body = logs["varLogs"] + node.body
        return [logs["logStmt"], meta_tag, node] 
    
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
        logs = self.generateLtLogStmts(node, False, "child")
        meta_tag = getTag(self.logTypeCount, "prev")
        self.generic_visit(node)
        node.body = [meta_tag, logs["logStmt"]] + logs["varLogs"] + node.body
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
    
    def visit_While(self, node):
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
        logs = self.generateLtLogStmts(node, False, "child")
        meta_tag = getTag(self.logTypeCount, "next")
        self.generic_visit(node)
        node.body = logs["varLogs"] + node.body + [logs["logStmt"]]
        return [logs["logStmt"], meta_tag, node]
    
    def visit_For(self, node):
        return self.injectLogTypesD(node)
    
    def visit_AsyncFor(self, node):
        return self.injectLogTypesD(node)


