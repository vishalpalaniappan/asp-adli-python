import ast
import uuid
from injector.VariableCollectors.BaseVariableCollector import VariableCollectorBase

class CollectAssignVarInfo(ast.NodeVisitor, VariableCollectorBase):
    '''
        Collects variable info from assign node targets. It also 
        extracts the keys of the target node.
    '''

    def __init__(self, node, logTypeId, funcId):
        VariableCollectorBase.__init__(self, logTypeId, funcId)
        self.node = node
        self.keys = []
        self.containsSlice = False
        self.generic_visit(ast.Module(body=[node], type_ignores=[]))
        
        if self.containsSlice:
            '''
            There isn't support for creating keys from slice nodes.
            So for now, we remove the keys and log the whole variable. 
            There will be further support added for this in the future.
            '''
            name = self.keys.pop(0)["value"]
            self.getVarInfo(name, [], name, None)
        elif len(self.keys) > 0:
            name = self.keys.pop(0)["value"]
            self.getVarInfo(name, self.keys, ast.unparse(self.node), None)
        
    def getVariableName(self):
        '''
            Generates a remporary variable name using the uuid module. This
            variable will be hidden from the user in the diagnostic log viewer.
        '''
        return "asp_temp_var_" + str(uuid.uuid1()).replace("-", "")

    def visit_Subscript(self, node):
        '''
            If any of the subscript nodes are an expression that need 
            to be evaluated, then create a temporary variable and replace
            the subscript with the name of the temporary variable. 
        '''
        if isinstance(node.slice, (ast.Slice, ast.Tuple)):
            self.generic_visit(node)
            self.containsSlice = True

        elif not isinstance(node.slice, (ast.Constant, ast.Name)):
            self.generic_visit(ast.Module(body=[node.value], type_ignores=[]))

            varName = self.getVariableName()
            self.keys.append({"type": "temp_variable", "value": varName})
            self.getVarInfo(varName, [], varName, node.slice)

            node.slice = ast.Name(id= varName, ctx=ast.Load())
        else:
            self.generic_visit(node)
        return node
    
    def visit_Name(self, node):
        self.generic_visit(node)
        self.keys.append({"type":"variable", "value":node.id})
        return node
    
    def visit_Attribute(self, node):
        self.generic_visit(node)
        self.keys.append({"type":"key", "value":node.attr})
        return node
    
    def visit_Constant(self, node):
        self.generic_visit(node)
        self.keys.append({"type":"key", "value":node.value})
        return node