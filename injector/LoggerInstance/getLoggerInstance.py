import ast
import os
from pathlib import Path

class SetUniqueId(ast.NodeTransformer):
    '''
        Given the AdliLogger.py file, this class
        updates the variable value of ADLI_UNIQUE_ID
        with the given uniqueid.
    '''

    def __init__(self, uniqueid):
        self.uniqueid = uniqueid

    def visit_Assign(self, node):
        isName = isinstance(node.targets[0], ast.Name)
        if (isName and (node.targets[0].id == "ADLI_UNIQUE_ID")):
            node.value = ast.Constant(value=self.uniqueid)
        return node
    

def getLoggerInstanceWithUid(uniqueid):
    '''
        Given a uniqueid, this function sets the unique id of
        AdliLogger.py and returns the unparsed source.
    '''
    path = Path(os.path.dirname(__file__)) / "AdliLogger.py"
    with open(path, "r") as f:
        source = f.read()
        tree = ast.parse(source)
        SetUniqueId(uniqueid).visit(tree)
        return ast.unparse(tree)


