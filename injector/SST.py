import ast

class SST:

    def __init__(self, ltCount):
        """
            Creates the root of the tree and initializes logTypeID.
        """
        self.tree = {
            "type": "root",
            "children": [],
            "siblings": [],
        }
        self.id = ltCount
        self.activeNode = self.tree

    def createSSTNode(self, type, syntax, lineno):
        """
            Creates an SST node with the provided arguments.
        """
        sstNode = {
            "type": type,
            "children": [],
            "siblings": [],
            "syntax": syntax,
            "id": self.id,
            "lineno": lineno
        }
        self.id += 1
        return sstNode
    
    def addAstNode(self, type, astNode, isSibling):
        """
            This function accepts a python AST node and creates
            a SST node which it adds to the active node. 

            Args:
                type: Node type from AST (root, child)
                node: AST Node
                isSibling: Indicates whether the node should be added 
                to the children or sibling array in the SST.
        """

        if isinstance(astNode.astNode, ast.FunctionDef):
            type = "function"

        # Add the logtype id to the astNode to use when generating log statements.
        astNode.id = self.id
        sstNode = self.createSSTNode(type, astNode.syntax, astNode.lineno)
        if (isSibling):
            self.activeNode["siblings"].append(sstNode)
        else:
            self.activeNode["children"].append(sstNode)

        return sstNode
    

    def addCustomNode(self, type, syntax, lineno, isSibling):
        """
            This function accepts a custom node and adds it to the
            SST. This is used because the python AST library does 
            not have nodes for else or finally blocks.
        """    
        sstNode = self.createSSTNode(type, syntax, lineno)

        if (isSibling):
            self.activeNode["siblings"].append(sstNode)
        else:
            self.activeNode["children"].append(sstNode)

        return sstNode