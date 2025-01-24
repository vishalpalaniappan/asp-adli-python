import ast
import copy
from injector.CollectVariableNames import CollectVariableNames

class NodeExtractor():
    """
        This class is used to process an AST node to extract
        the syntax. It is passed into the SST class to populate
        the SST nodes information. It also exposes functions to 
        generate the logging statements for this node. This will 
        be extended to support variables.
    """
    def __init__(self, node):
        self.lineno = node.lineno

        if 'body' in node._fields:
            if isinstance(node, ast.FunctionDef):
                self.type = "function"
            self.astNode = self.getEmptyASTRootNode(node)
            self.extractFromASTNode()
        else:
            self.astNode = node
            self.extractFromASTNode()

    def extractFromASTNode(self):
        """
            Creates an AST module and initializes it with the astNode.
            Unparses it to get the syntax and saves it.
        """
        module = ast.Module(body=[self.astNode], type_ignores=[])
        self.syntax = ast.unparse(ast.fix_missing_locations((module)))
        self.vars = CollectVariableNames(self.astNode).var_names 
            
    def getEmptyASTRootNode(self,node):
        """
            Removes all children from the AST node so that the syntax
            of the parent can be extracted.
        """
        n = copy.copy(node)
        keysToEmpty = ["body", "orelse","else","handlers","finalbody"]
        for key in keysToEmpty:
            if key in n._fields:
                setattr(n, key, [])
        return n
    
    def getVariableLogStatements(self):
        '''
            Returns a list of log statements for each variable.
        '''
        variableLogStmts = []
        for name in self.vars:
            logStr = f"logger.info(\"# {self.logTypeId} %s\", str({name}))"
            variableLogStmts.append(ast.parse(logStr))   
        return variableLogStmts
    
    def getLoggingStatement(self):
        """
            Generates a logging statement using the logtype.
        """
        return ast.Expr(
            ast.Call(
                func=ast.Name(id='logger.info', ctx=ast.Load()),
                args=[ast.Constant(value=self.logTypeId)],
                keywords=[]
            )
        )