import ast
import uuid
from injector.helper import getEncodedOutputStmt

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

def getVariableName():
    '''
        Generates a temporary variable name using the uuid module.
    '''
    return "asp_temp_var_" + str(uuid.uuid4()).replace("-", "")

def getAssignStmt(name, value):
    '''
        Returns an assign statement with the provided arguments.
    '''
    return ast.fix_missing_locations(ast.Assign(
        targets=[ast.Name(id=name, ctx=ast.Store)],
        value= value
    ))

class OutputWrapper(ast.NodeTransformer):

    def __init__(self, node, outputMeta):
        '''
        Initialies the output wrapper and visits the child nodes.
        
        :param self: 
        :param node: Node that is being transformed.
        :param outputMeta: Instrumented output metadata.
        '''
        self.node = node
        self.metaStmts = []
        self.outputMeta = outputMeta
        self.generic_visit(ast.Module(body=[node], type_ignores=[]))
    
    def visit_Call(self, node):
        '''
        Visit call nodes so that they can be transformed.

        - Finds function calls with the specified names
        - Assigns arguments to a temporary variable
        - Replaces function argument with a temporary variable
        
        :param self: 
        :param node: Node that is being visited and transformed.
        '''
        for output in self.outputMeta:
            if isValidCall(node, output["function"]):
                tempName = getVariableName()
                self.metaStmts.append(getAssignStmt(tempName, node.args[0]))
                self.metaStmts.append(getEncodedOutputStmt(tempName))
                node.args = [ast.Name(id=tempName, ctx=ast.Load())]

        return node