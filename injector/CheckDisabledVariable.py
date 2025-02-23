import re, ast

def getDisabledVariables(node):

    if "value" in node._fields and isinstance(node.value, ast.Constant):

        value = node.value.value
        variables = re.findall("adli-disable-variable (.*)", value)

        if len(variables) > 0:
            return variables[0].split()
        
    return []
        