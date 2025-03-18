import ast
from injector.VariableCollectors.BaseVariableCollector import VariableCollectorBase

class CollectFunctionArgInfo(ast.NodeVisitor, VariableCollectorBase):
    '''
        Collects the variable info for arguments to the function. 
        TODO: Remove this class once the feature to extract the
        arguments from call location are implemented.
    '''

    def __init__(self, node, logTypeId, funcId):
        VariableCollectorBase.__init__(self, logTypeId, funcId)
        self.generic_visit(node)
    
    def visit_arg(self, node):
        self.getVarInfo(node.arg, [], node.arg, None)
        self.generic_visit(node)