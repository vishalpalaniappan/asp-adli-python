import ast

def isValidCall(node, callName):
    '''
    Identifies if a function call with the specified name
    was found. It can be a name or an attributed:

    ex: put() or var.put()
    
    :param node: Node that is being inspected.
    :param callName: Function call that is targetted. 
    '''
    isName = isinstance(node.func, ast.Name)
    isAttr = isinstance(node.func, ast.Attribute)
    return ((isName and node.func.id == callName) or (isAttr and node.func.attr == callName))

class OutputWrapper(ast.NodeTransformer):

    def __init__(self, node, outputMeta):
        '''
        Initialies the output wrapper and visits the child nodes.
        
        :param self: 
        :param node: Node that is being transformed.
        :param outputMeta: Instrumented output metadata.
        '''
        self.node = node
        self.outputMeta = outputMeta
        self.generic_visit(ast.Module(body=[node], type_ignores=[]))
    
    def visit_Call(self, node):
        '''
        Visit call nodes so that they can be transformed.
        
        :param self: 
        :param node: Node that is being visited and transformed.
        '''
        for output in self.outputMeta:
            if isValidCall(node, output["function"]):
                print("Found function named", output["function"])

        return node