import ast
import json

def getMetadata(node):
    """
        This function checks if a comment contains ADLI metdata and if it does,
        it returns the metadata.

        Example:
        '''
        {
            "type": "adli_metadata",
            "name": "ADLI",
            "description": "A tool to inject diagnostic logs into a python program.",
            "version": "0.0",
            "language": "python"
        }
        '''
    """
    if "value" in node._fields and isinstance(node.value, ast.Constant):
        value = node.value.value

        try:
            obj = json.loads(value)

            if (obj["type"] == "adli_metadata"):
                return obj
        except:
            return None
        
    return None
