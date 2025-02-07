import ast
import copy
from injector import helper
from injector.CollectVariableNames import CollectVariableNames

VARIABLE_NODE_TYPES = (ast.Assign, ast.For, ast.FunctionDef)
VAR_COUNT = 0

class NodeExtractor():
    """
        This class is used to process an AST node to extract
        the syntax and variables. It also returns nodes with the
        injected log statements which are used by NodeTransformer
        to replace the original nodes.
    """
    def __init__(self, node, logType, logTypeFuncId):
        self.vars = []
        self.logTypeId = logType
        self.astNode = node
        self.extractFromASTNode()

        self.ltMap = {
            "id": logType,
            "funcid": logTypeFuncId,
            "syntax": self.syntax,
            "lineno": node.lineno,
            "type": "function" if isinstance(node, ast.FunctionDef) else "child",
            "vars": self.vars
        }

    def extractFromASTNode(self):
        '''
            Creates an AST module and initializes it with the astNode.
            Unparses it to get the syntax/variables. For nodes with 
            a body, it removes all children before extracting the syntax
            and variables. 
        '''
        global VAR_COUNT

        if 'body' in self.astNode._fields:
            node = helper.getEmptyRootNode(self.astNode)
        else:
            node = self.astNode

        module = ast.Module(body=[node], type_ignores=[])
        self.syntax = ast.unparse(ast.fix_missing_locations((module)))

        if isinstance(node, VARIABLE_NODE_TYPES):
            for var in CollectVariableNames(node).var_names:
                VAR_COUNT += 1
                self.vars.append({
                    "varId": VAR_COUNT,
                    "name": var
                })
    
    def getVariableLogStatements(self):
        '''
            Returns a list of log statements for each variable.
        '''
        variableLogStmts = []
        for varObj in self.vars:
            name = varObj["name"]
            varId = varObj["varId"]
            logStr = f"aspAdliLog({name}, {varId})"
            variableLogStmts.append(ast.parse(logStr))   
        return variableLogStmts
    
    def getLoggingStatement(self):
        '''
            Generates a logging statement using the logtype.
        '''
        return ast.Expr(
            ast.Call(
                func=ast.Name(id='logger.info', ctx=ast.Load()),
                args=[ast.Constant(value=self.logTypeId)],
                keywords=[]
            )
        )

    def getInjectedNodes(self):
        '''
            Returns a list with injected log statements 
            to add to the tree.
            
            Example:
                logger.info(<logtype_id>)
                <original_ast_node>
        '''
        nodes = [
            self.getLoggingStatement(),
            self.astNode,
            self.getVariableLogStatements()
        ]
        return nodes

    def getInjectedNodesIf(self):
        '''
            Returns a list with injected log statements 
            for if nodes to add to the tree.
            
            Example:
                logger.info(<logtype_id>)
                if <expression>:
                    ...
        '''
        self.astNode.body.insert(0, self.getVariableLogStatements())
        nodes = [
            self.getLoggingStatement(),
            self.astNode
        ]
        return nodes
    
    def getInjectedNodesFunc(self):
        '''
            Returns a list with injected log statements 
            to add to the tree for functions.
            
            Example:
                def function():
                    logger.info(<logtype_id>)
                    ...
        '''
        self.astNode.body.insert(0, self.getLoggingStatement())
        return self.astNode
    
    def getInjectedNodesFor(self):
        '''
            Returns a list with injected log statements 
            to add to the tree for FOR nodes.
            
            Example:
                logger.info(<logtype_id>)
                for i in numbers:
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
    
    def getInjectedNodesWhile(self):
        '''
            Returns a list with injected log statements 
            to add to the tree for WHILE nodes.
            
            Example:
                logger.info(<logtype_id>)
                while (i < 10):
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