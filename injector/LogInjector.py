import ast
from injector.NodeExtractor import NodeExtractor

class LogInjector(ast.NodeTransformer):
    def __init__(self, node, ltMap, logTypeCount):
        self.logTypeCount = logTypeCount
        self.minLtCount = self.logTypeCount
        self.funcLogType = 0
        self.ltmap = ltMap
        self.generic_visit(node)
        self.maxLtCount = self.logTypeCount

    def processNode(self, node):
        '''
            This function is called on every visit.
            It passes the node to the node extractor,
            adds to the ltMap and returns the node
            extractor object.
        '''
        self.logTypeCount += 1
        _node = NodeExtractor(node, self.logTypeCount, self.funcLogType)
        self.ltmap[self.logTypeCount] = _node.ltMap
        return _node
    
    def visit_FunctionDef(self, node):
        '''
            When visiting functions, set the function id so 
            that when we continue walking, we can use it to set 
            the function id of child nodes. Reset the function
            id to 0 (global scope) after visiting children.
        '''
        self.funcLogType = self.logTypeCount + 1
        _node = self.processNode(node)
        self.generic_visit(node)
        self.funcLogType = 0
        return _node.injectLogsTypeC()

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)
    
    '''
        INJECT LOGS TYPE A
        Example:
                logger.info(<logtype_id>)
                <original_ast_node>
                logger.info(<var_id_1>)
                ...
                logger.info(<var_id_n>)
    '''
    def visit_Raise(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeA()
    
    def visit_Return(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeA()

    def visit_Import(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeA()
    
    def visit_ImportFrom(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeA()

    def visit_Expr(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeA()
    
    def visit_Assign(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeA()

    def visit_AugAssign(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeA()

    '''
        INJECT LOGS TYPE B
        Example:
            logger.info(<logtype_id>)
            if <expression>:
                logger.info(<var_id_1>)
                ...
                logger.info(<var_id_n>)
    '''
    def visit_With(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeB()

    def visit_If(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeB()
    
    '''
        INJECT LOGS TYPE C
        Example
            def func_1():
                logger.info(<logtype_id>)
                ...
                logger.info(<var_id_1>)
                logger.info(<var_id_n>):
    '''
    def visit_ClassDef(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeC()
    
    def visit_Try(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeC()

    def visit_TryFinally(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeC()

    def visit_TryExcept(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeC()

    def visit_ExceptHandler(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeC()
    
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
    def visit_For(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeD()
    
    def visit_While(self, node):
        self.generic_visit(node)
        return self.processNode(node).injectLogsTypeD()