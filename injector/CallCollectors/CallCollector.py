import ast
from injector.helper import getEmptyRootNode

class FunctionCallCollector(ast.NodeVisitor):
    '''
        Given a statement, this class extracts all the 
        function calls that were made. 
        
        Ex: print(bar(baz(2)), qux())
        Calls: ['print', 'bar', 'baz', 'qux']    
    '''
    def __init__(self, node):
        self.calls = []
        self.async_calls = []

        if 'body' in node._fields:
            node = getEmptyRootNode(node)

        self.generic_visit(ast.Module(body=[node], type_ignores=[]))


    def visit_Call(self, node):
        '''
            Visit call nodes and save the function
            calls to a list.

            If the function call is async, then append
            to async_calls and if not, append it to calls.
        '''
        func_name = self._getFuncName(node.func)

        if isinstance(getattr(node, 'parent', None), ast.Await):
            self.async_calls.append(func_name)
        else:
            self.calls.append(func_name)
        self.generic_visit(node)

    def visit_Await(self, node):
        '''
            When visiting a function await node,
            tag the function call to indicate that
            this is an async func call.
        '''
        if isinstance(node.value, ast.Call):
            node.value.parent = node
        self.generic_visit(node)

    def _getFuncName(self, node):
        '''
            Get the function name.
        '''
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None