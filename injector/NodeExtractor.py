import ast
import copy
from injector import helper
from injector.CollectVariableNames import CollectVariableNames


class NodeExtractor():
    """
        This class is used to process an AST node to extract
        the syntax and variables. It also returns nodes with the
        injected log statements which are used by NodeTransformer
        to replace the original nodes.
    """
    def __init__(self, node, logType, logTypeFuncId, globalsInFunc, globalDisabledVars, disabledVars):
        self.vars = []
        self.logTypeId = logType
        self.astNode = node

        self.fId = logTypeFuncId
        self.globalsInFunc = globalsInFunc
        self.globalDisabledVars = globalDisabledVars
        self.disabledVars = disabledVars

        self.extractFromASTNode()

        self.ltMap = {
            "id": logType,
            "funcid": logTypeFuncId,
            "syntax": self.syntax,
            "lineno": node.lineno,
            "end_lineno": node.end_lineno,
            "type": "child",
            "vars": self.vars
        }

        if isinstance(node, ast.FunctionDef):
            self.ltMap["type"] = "function"
            self.ltMap["name"] = node.name

    def extractFromASTNode(self):
        '''
            Creates an AST module and initializes it with the astNode.
            Unparses it to get the syntax/variables. For nodes with 
            a body, it removes all children before extracting the syntax
            and variables. 
        '''
        if 'body' in self.astNode._fields:
            node = helper.getEmptyRootNode(self.astNode)
        else:
            node = self.astNode

        module = ast.Module(body=[node], type_ignores=[])
        self.syntax = ast.unparse(ast.fix_missing_locations((module)))
        self.vars = CollectVariableNames(node).vars

        self.vars = self.removeDisabledVariables(self.vars)

        for var in self.vars:
            var["global"] = var["name"] in self.globalsInFunc

    def removeDisabledVariables(self, vars):
        '''
            Checks if the variable is disabled.
             
            Conditions:
            - If in global scope and global variable is disabled 
            - If global is defined in func and global variable is disabled
            - If variable is disabled in function
        '''
        varList = []
        for var in vars:
            if (var["name"] in self.globalDisabledVars):
                if (self.fId == 0 or var["name"] in self.globalsInFunc):
                    continue
            elif (var["name"] in self.disabledVars):
                continue
            varList.append(var)

        return varList

    
    def getVariableLogStatements(self):
        '''
            Returns a list of log statements for each variable.
        '''
        variableLogStmts = []
        for varObj in self.vars:
            name = varObj["name"]
            varId = varObj["varId"]
            variableLogStmts.append(helper.getVariableLogStatement(name, varId))   
        return variableLogStmts
    
    def getLoggingStatement(self):
        '''
            Generates a logging statement using the logtype id.
        '''
        return ast.Expr(
            ast.Call(
                func=ast.Name(id='logger.info', ctx=ast.Load()),
                args=[ast.Constant(value=self.logTypeId)],
                keywords=[]
            )
        )

    def injectLogsTypeA(self) -> list[ast.AST]:
        '''
            Example:
                logger.info(<logtype_id>)
                <original_ast_node>
        '''
        nodes = [
            self.getLoggingStatement(),
            self.astNode,
        ]
        return nodes

    def injectLogsTypeB(self) -> list[ast.AST]:
        '''
            Example:
                logger.info(<logtype_id>)
                <original_ast_node>
                logger.info(<var_id_1>)
                ...
                logger.info(<var_id_n>)
        '''
        nodes = [
            self.getLoggingStatement(),
            self.astNode,
            self.getVariableLogStatements()
        ]
        return nodes

    def injectLogsTypeC(self) -> list[ast.AST]:
        '''
            Example:
                logger.info(<logtype_id>)
                if <expression>:
                    logger.info(<var_id_1>)
                    ...
                    logger.info(<var_id_n>)
        '''
        self.astNode.body.insert(0, self.getVariableLogStatements())
        nodes = [
            self.getLoggingStatement(),
            self.astNode
        ]
        return nodes

    def injectLogsTypeD(self) -> list[ast.AST]:
        '''
            Example:
                def func_1():
                    logger.info(<logtype_id>)
                    ...
                    logger.info(<var_id_1>)
                    logger.info(<var_id_n>)
        '''
        self.astNode.body.insert(0, self.getLoggingStatement())
        self.astNode.body.insert(1, self.getVariableLogStatements())
        return [self.astNode]

    def injectLogsTypeE(self) -> list[ast.AST]:
        '''
            Example:
                logger.info(<logtype_id>)
                for <expression>:
                    logger.info(<var_id_1>)
                    logger.info(<var_id_n>)
                    ...
                    logger.info(<logtype_id>)
        '''
        self.astNode.body.append(self.getLoggingStatement())
        self.astNode.body.insert(0, self.getVariableLogStatements())
        nodes = [
            self.getLoggingStatement(),
            self.astNode
        ]
        return nodes