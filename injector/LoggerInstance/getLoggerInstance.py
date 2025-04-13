import ast
import os
from pathlib import Path

def getLoggerInstance():
    '''
        Given a uniqueid, this function sets the unique id of
        AdliLogger.py and returns the unparsed source.
    '''
    path = Path(os.path.dirname(__file__)) / "AdliLogger.py"
    with open(path, "r") as f:
        source = f.read()
        tree = ast.parse(source)
        return ast.unparse(tree)


