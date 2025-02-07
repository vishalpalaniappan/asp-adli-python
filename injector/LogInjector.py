import ast
from injector.NodeExtractor import NodeExtractor

LOG_TYPE_COUNT = 0

class LogInjector(ast.NodeTransformer):
    def __init__(self, node, ltMap):
        self.minLtCount = LOG_TYPE_COUNT + 1
        self.funcLogType = 0
        self.ltmap = ltMap
        self.generic_visit(node)
        self.maxLtCount = LOG_TYPE_COUNT

    def processNode(self, node):
        '''
            This function is called on every visit.
            It passes the node to the node extractor,
            adds to the ltMap and returns the node
            extractor object.
        '''
        global LOG_TYPE_COUNT
        LOG_TYPE_COUNT = LOG_TYPE_COUNT + 1
        _node = NodeExtractor(node, LOG_TYPE_COUNT, self.funcLogType)
        self.ltmap[LOG_TYPE_COUNT] = _node.ltMap
        return _node
    
    def visit_FunctionDef(self, node):
        '''
            When visiting functions, set the function id so 
            that when we continue walking, we can use it to set 
            the function id of child nodes. Reset the function
            id to 0 (global scope) after visiting children.
        '''
        global LOG_TYPE_COUNT
        self.funcLogType = LOG_TYPE_COUNT + 1
        _node = self.processNode(node)
        self.generic_visit(node)
        self.funcLogType = 0
        return _node.getInjectedNodesFunc()

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)
    
    def visit_Raise(self, node):
        _node = self.processNode(node)
        return _node.getInjectedNodes()
    
    def visit_Return(self, node):
        _node = self.processNode(node)
        return _node.getInjectedNodes()

    def visit_Import(self, node):
        _node = self.processNode(node)
        return _node.getInjectedNodes()
    
    def visit_ImportFrom(self, node):
        _node = self.processNode(node)
        return _node.getInjectedNodes()

    def visit_Expr(self, node):
        _node = self.processNode(node)
        return _node.getInjectedNodes()

    def visit_If(self, node):
        _node = self.processNode(node)
        self.generic_visit(node)
        return _node.getInjectedNodesIf()
    
    def visit_Assign(self, node):
        _node = self.processNode(node)
        return _node.getInjectedNodes()

    def visit_AugAssign(self, node):
        _node = self.processNode(node)
        return _node.getInjectedNodes()
    
    def visit_For(self, node):
        _node = self.processNode(node)
        self.generic_visit(node)
        return _node.getInjectedNodesFor()
    
    def visit_While(self, node):
        _node = self.processNode(node)
        self.generic_visit(node)
        return _node.getInjectedNodesWhile()
    
    def visit_ClassDef(self, node):
        _node = self.processNode(node)
        self.generic_visit(node)
        return _node.getInjectedNodes()
    
    def visit_Try(self, node):
        _node = self.processNode(node)
        self.generic_visit(node)
        return _node.getInjectedNodesFunc()

    def visit_TryFinally(self, node):
        _node = self.processNode(node)
        self.generic_visit(node)
        return _node.getInjectedNodesFunc()

    def visit_TryExcept(self, node):
        _node = self.processNode(node)
        self.generic_visit(node)
        return _node.getInjectedNodesFunc()

    def visit_ExceptHandler(self, node):
        _node = self.processNode(node)
        self.generic_visit(node)
        return _node.getInjectedNodesFunc()

    def visit_With(self, node):
        _node = self.processNode(node)
        self.generic_visit(node)
        return _node.getInjectedNodesIf()