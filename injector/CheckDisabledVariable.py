import re, ast

def isDisabledVariable(node):

    if "value" in node._fields and isinstance(node.value, ast.Constant):

        value = node.value.value
        variables = re.findall("asp-adli-disable-variable (.*)", value)

        if len(variables) > 0:
            print(variables)
        