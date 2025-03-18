import ast
import uuid
from injector.VariableCollectors.BaseVariableCollector import VariableCollectorBase
from injector.helper import getEmptyRootNode

class CollectCallVariables(ast.NodeVisitor, VariableCollectorBase):
    '''
        This class visits all Call nodes and extracts the variable names
        as well as the keys.
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
                self.generic_visit(ast.Module(body=[childNode.func], type_ignores=[]))
                self.saveVariableInfo(childNode.func)

    def saveVariableInfo(self, childNode):
        '''
            Save the variable info if the necessary conditions are met:
            - At least one key was found (first key is the variable name)
            - The variable exists in the current stack
            - If the variable containes a slice, log the entire variable

            a["b"]["c"].append(1)
            keys = [
                {type:"variable",value:a},
                {type:"key",value:"b"},
                {type:"key",value:"c"},
                {type:"key",value:"append"}
            ]

            - Name is first element in the keys list.
            - The last element is the function call and it needs to be removed.
            - The syntax will be a["b"]["c"].append, so we need to remove everything 
              to the right of the final dot.
        '''
        if len(self.keys) <= 1:
            return
        
        name = self.keys.pop(0)["value"]
        self.keys.pop()

        if self.containsSlice:
            self.getVarInfo(name, [], name, None)
            return

        if self.isValidVariableName(name):
            syntax = ast.unparse(childNode)
            if ("." in syntax):
                syntax = ''.join(syntax.rpartition('.')[:-2])
            self.getVarInfo(name, self.keys, syntax, None)
            return

    def isValidVariableName(self, name):
        '''
            Check if the variable name is in the current stack.
        '''
        for varKey in self.existingVars:
            if name == self.existingVars[varKey]["name"]:
                return True
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