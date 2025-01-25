import ast
import os
import pathlib
from injector import helper
from injector.NodeExtractor import NodeExtractor
from injector.SST import SST

class LogInjector:
    """
        This class is used to inject diagnostic logs into a given sourcefile.
        It parses the source code into an AST and recursively processes the 
        AST until all nodes are consumed while building a simplified syntax
        tree and injected the necessary logging statements. 

        The NodeExtractor class is used to process an AST node and extract the 
        necessary information. The SST class accepts a NodeExtractor object and 
        uses the extracted information to populate the SST.
    """
    def __init__(self, sourcePath, ltCount):
        self.sourcePath = sourcePath
        self.sourceDir = os.path.dirname(sourcePath)
        self.fileNameWExtension = os.path.basename(sourcePath)
        self.fileName = pathlib.Path(sourcePath).stem
        with open(sourcePath, "r") as f:
            self.source = f.read()

        self.sourcetree = ast.parse(self.source)

        # Surround file with try except structure
        mainTry = ast.Try(body=[],handlers=[], orelse=[],finalbody=[])
        mainTry.handlers.append(helper.getExceptionLog(0))
        self.injectedTree = ast.Module( body=[mainTry], type_ignores=[])

        self.importsFound = []

        self.sst = SST(ltCount)
    def run(self):
        """
            Runs the injector and returns the SST and injected code.
        """
        mainTryBody = self.injectedTree.body[0].body
        self.processTree(self.sourcetree.body, mainTryBody)
    
    def processRootNode(self, rootNode, injectedTree, isSibling):
        '''
            Given an root AST node (if, while, def etc.), this function
            inserts the node into the SST. It then adds the node into the
            injected tree and adds the corresponding log statements. It 
            then processes the body of the the root node.

            :param rootNode: AST Node which contains body nodes
            :param injectedTree: AST Module to inject logs into
            :param isSibling: Indicates if this node is a sibling 
                node (elif, else,except etc)
        '''
        node = NodeExtractor(rootNode)
        sstRootNode = self.sst.addAstNode("root", node, isSibling)
        self.sst.activeNode = sstRootNode

        node.astNode.body.insert(0, node.getLoggingStatement())
        if len(node.vars) > 0:
            for stmt in reversed(node.getVariableLogStatements()):
                node.astNode.body.insert(1, stmt)
        injectedTree.append(node.astNode)
        self.processTree(rootNode.body, node.astNode.body)

        return sstRootNode

    def processChildNode(self, childNode, injectedTree):
        '''
            Given a child AST node, this function adds the node into
            sst. It then inserts the node and the corresponding log 
            statements into the injected tree. If the node is of type 
            import, it is processed to check for locally imported files.
        '''
        node = NodeExtractor(childNode)
        self.sst.addAstNode("child", node, False)
        
        injectedTree.append(node.getLoggingStatement())
        injectedTree.append(childNode)
        
        if len(node.vars) > 0:
            injectedTree.extend(node.getVariableLogStatements())

        self.importsFound += helper.checkImport(self.sourceDir, childNode)
    
    def processIfStatement(self, ifNode, injectedTree):
        '''
            Processes an if statement node. The elif and else statements
            are added as siblings to the if root node.
        '''
        #Process if block
        sstRootNode = self.processRootNode(ifNode, injectedTree, False)
        self.sst.activeNode = sstRootNode
        
        #Process elif blocks
        next = ifNode.orelse
        injectedNode = injectedTree[-1]
        while len(next) > 0 and isinstance(next[0], ast.If):
            self.processRootNode(next[0], injectedNode.orelse, True)
            self.sst.activeNode = sstRootNode
            next = next[0].orelse
            injectedNode = injectedNode.orelse[0]

        #Process else block
        if "next" in ifNode._fields:
            self.sst.activeNode = self.sst.addCustomNode("root", "else:", None, True)
            for child in ifNode.next:
                self.processChildNode(child, injectedNode.next)
            
            
    def processTryStatement(self, tryNode, injectedTree):
        '''
            Processes the try ast instance. The exception handlers, else
            and finally blocks are added as siblings to the main try node.
        '''
        sstRootNode = self.processRootNode(tryNode, injectedTree, False)
        injectedNode = injectedTree[-1]

        for handler in tryNode.handlers:
            self.sst.activeNode = sstRootNode
            self.processRootNode(handler, injectedNode.handlers, True)

        if len(tryNode.orelse) > 0:
            self.sst.activeNode = sstRootNode
            self.sst.activeNode = self.sst.addCustomNode("root", "else:", None, True)
            for child in tryNode.orelse:
                self.processChildNode(child, injectedNode.orelse)

        if len(tryNode.finalbody) > 0:
            self.sst.activeNode = sstRootNode
            self.sst.activeNode = self.sst.addCustomNode("root", "finally:", None, True)
            for child in tryNode.finalbody:
                self.processChildNode(child, injectedNode.finalbody)

    def processTree(self,sourceTree, injectedTree):
        '''
            Processes an abstract syntax tree by recursively calling 
            this function on child elements until the tree is consumed.
            As the sourcetree is traversed the nodes are copied from 
            source to injected tree with the corresponding log statements.

            Args:
                sourceTree: List of AST nodes to process
                injectedTree: List to inject the processed nodes
        '''
        for node in sourceTree:
            if 'body' in node._fields:
                sstRootNode = self.sst.activeNode
                if isinstance(node,ast.Try):
                    self.processTryStatement(node,injectedTree)
                elif isinstance(node, ast.If):
                    self.processIfStatement(node,injectedTree)
                else:               
                    self.processRootNode(node, injectedTree, False) 
                self.sst.activeNode = sstRootNode
            else: 
                self.processChildNode(node, injectedTree)