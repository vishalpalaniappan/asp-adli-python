import ast
from injector.NodeExtractor import NodeExtractor

# These imports are added when injecting logging setup 
# and don't need to be imported twice.
IMPORTS_TO_IGNORE = [
    "import traceback",
    "import logging",
    "import json",
    "import sys"
]

class LogInjector(ast.NodeTransformer):
    def __init__(self, node, ltMap, logTypeCount):
        self.logTypeCount = logTypeCount
        self.minLtCount = self.logTypeCount
        self.funcLogType = 0
        self.ltmap = ltMap
        self.globalsInFunc = []
        self.generic_visit(node)
        self.maxLtCount = self.logTypeCount

    def processNode(self, node):
        '''
            This function is called on every visit.
            It passes the node to the node extractor,
            adds to the ltMap and returns the node
            with the extracted data for injecting logs.
        '''
        self.logTypeCount += 1
        _node = NodeExtractor(node, self.logTypeCount, self.funcLogType, self.globalsInFunc)
        self.ltmap[self.logTypeCount] = _node.ltMap
        return _node
    
    def visit_FunctionDef(self, node):
        '''
            When visiting functions, set the function id so 
            that when we continue visiting nodes, we can use it
            to set the function id of child nodes. Reset the
            function id to 0 (global scope) after visiting children.
        '''
        self.funcLogType = self.logTypeCount + 1
        _node = self.processNode(node)
        self.generic_visit(node)
        self.funcLogType = 0
        self.globalsInFunc = []
        return _node.injectLogsTypeD()

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)
    
    '''
        INJECT LOGS TYPE A
        Example:
            logger.info(<logtype_id>)
            <original_ast_node>

        INJECT LOGS TYPE B
        Example:
            logger.info(<logtype_id>)
            <original_ast_node>
            logger.info(<var_id_1>)
            ...
            logger.info(<var_id_n>)
    '''
    def visit_Assign(self, node):
        return self.processNode(node).injectLogsTypeB()
    
    def visit_Pass(self, node):
        return self.processNode(node).injectLogsTypeB()
    
    def visit_Global(self, node):
        self.globalsInFunc += node.names
        return self.processNode(node).injectLogsTypeB()
    
    def visit_Delete(self, node):
        return self.processNode(node).injectLogsTypeB()
    
    def visit_Nonlocal(self, node):
        return self.processNode(node).injectLogsTypeB()
    
    def visit_Break(self, node):
        return self.processNode(node).injectLogsTypeB()
    
    def visit_Continue(self, node):
        return self.processNode(node).injectLogsTypeB()
    
    def visit_Assert(self, node):
        return self.processNode(node).injectLogsTypeB()

    def visit_Raise(self, node):
        return self.processNode(node).injectLogsTypeB()
    
    def visit_Return(self, node):
        return self.processNode(node).injectLogsTypeB()

    def visit_Import(self, node):
        if (ast.unparse(node) in IMPORTS_TO_IGNORE):
            return
        return self.processNode(node).injectLogsTypeB()
    
    def visit_ImportFrom(self, node):
        if (ast.unparse(node) in IMPORTS_TO_IGNORE):
            return
        return self.processNode(node).injectLogsTypeB()

    def visit_Expr(self, node):
        return self.processNode(node).injectLogsTypeB()

    def visit_AugAssign(self, node):
        return self.processNode(node).injectLogsTypeB()
    
    def visit_AnnAssign(self, node):
        if "value" in node._fields and node.value == None:
            return self.processNode(node).injectLogsTypeA()
        else:
            return self.processNode(node).injectLogsTypeB()

    '''
        INJECT LOGS TYPE C
        Example:
            logger.info(<logtype_id>)
            if <expression>:
                logger.info(<var_id_1>)
                ...
                logger.info(<var_id_n>)
    '''
    def visit_With(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeC()
    
    def visit_AsyncWith(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeC()

    def visit_If(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeC()
    
    '''
        INJECT LOGS TYPE D
        Example
            def func_1():
                logger.info(<logtype_id>)
                ...
                logger.info(<var_id_1>)
                logger.info(<var_id_n>):
    '''
    def visit_ClassDef(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeD()
    
    def visit_Try(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeD()

    def visit_TryFinally(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeD()

    def visit_TryExcept(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeD()

    def visit_ExceptHandler(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeD()
    
    '''
        INJECT LOGS TYPE E
        Example:
            logger.info(<logtype_id>)
            for <expression>:
                logger.info(<var_id_1>)
                logger.info(<var_id_n>)
                ...
                logger.info(<logtype_id>)
    '''    
    def visit_For(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeE()
    
    def visit_AsyncFor(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeE()
    
    def visit_While(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeE()