import ast
import uuid
from injector.VariableCollectors.BaseVariableCollector import VariableCollectorBase
from injector.helper import getEmptyRootNode

class CollectCallVariables(ast.NodeVisitor, VariableCollectorBase):
    '''
        This class visits all Call nodes and extracts the variable names
        with keys.
    '''

    def __init__(self, node, logTypeId, funcId, existingVariables):
        VariableCollectorBase.__init__(self, logTypeId, funcId)
        self.keys = []
        self.existingVars = existingVariables
        self.containsSlice = False

        if 'body' in node._fields:
            node = getEmptyRootNode(node)

        # Process any child nodes if they are call instances
        for childNode in ast.walk(node):
            if isinstance(childNode, ast.Call):
                self.generic_visit(childNode.func)
                self.saveVariableInfo(childNode)

    def saveVariableInfo(self, childNode):
        '''
            Save the variable info if the necessary conditions are met.
            Conditions are:
            - At least one key was found (first key is the name)
            - The variable exists in the current stack

            If variable containes a slice, log the entire variable
            
            Before saving variable info, remove the function call from the syntax.
        '''
        if self.containsSlice:
            name = self.keys.pop(0)["value"]
            self.getVarInfo(name, [], name, None)

        elif len(self.keys) > 0:
            name = self.keys.pop(0)["value"]
            if self.isValidVariableName(name):
                syntax = ''.join(ast.unparse(childNode.func).rpartition('.')[:2])[:-1]
                self.getVarInfo(name, self.keys, syntax, None)

    def isValidVariableName(self, name):
        '''
            Check if the variable that was identified exists in the current stack.
        '''
        for varKey in self.existingVars:
            return name == self.existingVars[varKey]["name"]
        return False
        
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