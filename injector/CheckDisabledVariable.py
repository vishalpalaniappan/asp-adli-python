import re, ast

def getDisabledVariables(node):
    '''
        This function parses the variable disable comments and returns
        a list with the disabled variables. 

        It parses triple quote comments. 
        Example:
        \'\'\'adli-variable-disable value variables\'\'\'
    '''
    
    disabledVariables = []
    if "value" in node._fields and isinstance(node.value, ast.Constant):

        value = node.value.value
        variables = re.findall("adli-disable-variable (.*)", value)

        if len(variables) > 0:
            disabledVariables = variables[0].split()
        
    return disabledVariables
        