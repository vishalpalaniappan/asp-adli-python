import re
import ast

def getDisabledVariables(node):
    """
        This function parses the variable disable comments and returns
        a list with the disabled variable names.

        Currently, the python AST library only supports parsing triple
        quote comments.
        
        Example:
        '''adli-disable-variable varName1 varName2 varNameN'''
    """
    
    disabledVariables = []
    if "value" in node._fields and isinstance(node.value, ast.Constant):

        value = node.value.value

        variables = re.findall("adli-disable-variable (.*)", value)
        if len(variables) > 0:
            disabledVariables = variables[0].split()
            return disabledVariables
        
    return disabledVariables
