import ast
import os

class ImportVisitor(ast.NodeVisitor):
    """
        Visit all import statements and find locally imported files.
    """
    def __init__(self, node, rootDir):
        self.rootDir = rootDir
        self.importsFound = []
        self.generic_visit(node)

    def visit_Import(self, node):
        importsFound = checkImport(self.rootDir, node)
        if len(importsFound) > 0:
            self.importsFound = self.importsFound + importsFound

    def visit_ImportFrom(self, node):
        importsFound = checkImport(self.rootDir, node)
        if len(importsFound) > 0:
            self.importsFound = self.importsFound + importsFound
    
def checkImport(rootDir, node):
    """
        Check if an import statement refers to a local file.

        Args:
            rootDir (str): The root directory to resolve relative imports
            node (ast.Import | ast.ImportFrom): The AST node representing the import

        Returns:
            list[str]: List of valid local file paths

        Example:
            >>> node = ast.parse("import foo.bar").body[0]
            >>> checkImport("/root", node)
            ['/root/foo/bar.py']
    """
    pathsToCheck = []
    if isinstance(node, ast.Import):
        name = node.names[0].name.replace('.', '/')
        path = os.path.join(rootDir, name + '.py')
        pathsToCheck.append(path)
    elif isinstance(node, ast.ImportFrom):
        module = os.path.join(rootDir, node.module.replace('.', '/'))
        name = os.path.join(node.names[0].name.replace('.', '/'))
        pathsToCheck.append(f"{module}/{name}.py")
        pathsToCheck.append(f"{module}.py")
    
    # Check for valid paths
    validPaths = []
    for path in pathsToCheck:
        try:
            with open(path) as f:
                validPaths.append(path)
        except FileNotFoundError:
            # Skip if file doesn't exist
            continue
        except (IOError, PermissionError) as e:
            print(f"Warning: Failed to check {path}: {e}")
            continue

    return validPaths
def findLocalImports(sourceFile):
    """
        Find and returns all local imports associated with the source file.
    """
    rootDir = os.path.dirname(sourceFile)
    pathsFound = []
    fileQueue = [sourceFile]

    while len(fileQueue) > 0:
        sourceFile = fileQueue.pop()
        try:
            with open(sourceFile, "r") as f:
                source = f.read()
        except IOError as e:
            raise IOError(f"Failed to read source file {sourceFile}: {str(e)}") from e
        
        pathsFound.append(sourceFile)        

        for path in ImportVisitor(ast.parse(source), rootDir).importsFound:
            if path not in fileQueue and path not in pathsFound:
                fileQueue.append(path)

    return pathsFound