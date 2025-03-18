import ast
from injector.VariableCollectors.BaseVariableCollector import VariableCollectorBase
from injector.helper import getEmptyRootNode

class CollectVariableDefault(ast.NodeVisitor, VariableCollectorBase):
    '''
        This class collects any name nodes in the provided node. For
        nodes with a body, it removes the children before finding 
        the valid names. For example, in the case of a for loop,
        this would log the variable info for the current element in
        the loop.
    '''

    def __init__(self, node, logTypeId, funcId):
        VariableCollectorBase.__init__(self, logTypeId, funcId)

        if 'body' in node._fields:
            emptyNode = getEmptyRootNode(node)
            self.generic_visit(emptyNode)
        else:
            self.generic_visit(node)
    
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.getVarInfo(node.id, [], node.id, None)
        self.generic_visit(node)