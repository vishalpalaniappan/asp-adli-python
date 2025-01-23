from injector import helper
import pathlib
import shutil
import json
import ast
import os
from injector.LogInjector import LogInjector

class ProgramProcessor:
    '''
        This class accepts a source file and processes it and any local
        imports found using the log injector. It then writes the injected
        source files to the output directory.
    '''

    def __init__(self, sourceFile):
        self.sourceFile = sourceFile
        self.sourceName = pathlib.Path(sourceFile).stem
        self.sourceDir = os.path.dirname(sourceFile)
        self.fileTree = {}
        self.logTypeCount = 1
        self.injectors = []
        self.fileQueue = [sourceFile]

    def run(self, output_dir: str = "output"):
        '''
            Injects logs into files in the queue and add to file tree.
            Any local imports found when processing a file is added to
            the queue.
        '''
        while len(self.fileQueue) > 0: 
            inj = LogInjector(self.fileQueue.pop(), self.logTypeCount)
            inj.run()
            self.injectors.append(inj)

            self.fileTree[inj.sourcePath] = {
                "sst": inj.sst.tree,
                "source": inj.source,
            }

            self.addToQueue(inj.importsFound)
            self.logTypeCount = inj.sst.logTypeId

        # Create output folder if it doesn't exist
        outputFolder = os.path.join(os.getcwd(), output_dir)
        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder)
                  
        # Write each injected source to file
        for inj in self.injectors:
            currFolder = os.path.join(outputFolder, inj.sourceDir)
            if not os.path.exists(currFolder):
                os.makedirs(currFolder)

            if (self.sourceFile == inj.sourcePath):
                source = self.getInjectedSourceRoot(inj, inj.fileName)
            else:
                source = self.getInjectedSource(inj)

            filePath = os.path.join(currFolder, inj.fileNameWExtension)
            with open(filePath, "w+") as f:
                f.write(source)
        


    def addToQueue(self, paths):
        '''
            Adds the given paths to the queue if it is not already in the queue
            or if it hasn't already been processed.
        '''
        for currentImport in paths:
            if currentImport not in self.fileQueue and currentImport not in self.fileTree:
                self.fileQueue.append(currentImport)     
            

    def getInjectedSource(self, inj):
        '''
            Given an injector object, this funtion returns 
            a program injected with diagnostic logs.
        '''
        loggingSetupNodes = helper.getLoggingSetup()
        injectedSourceNodes = inj.injectedTree.body

        injectedNodes = loggingSetupNodes.body + injectedSourceNodes
        return ast.unparse(injectedNodes)

    def getInjectedSourceRoot(self, inj, fileName):
        '''
            Given an injector object, this funtion returns 
            a program injected with diagnostic logs.

            Args:
                inj: Injector object containing the processed AST
                fileName: Name for the logger setup
            
            Returns:
                str: The injected source code as a string
        '''
        loggingSetupNodes = helper.getRootLoggingSetup(str(fileName))
        fileTreeNodes = [
            helper.getLoggingStatement(
                json.dumps(self.fileTree))
        ]
        injectedSourceNodes = inj.injectedTree.body

        injectedNodes = loggingSetupNodes.body + fileTreeNodes + injectedSourceNodes
        return ast.unparse(injectedNodes)
    
    def clearAndCreateFolder (self, path):
        '''
            If folder exists, clear it and create it again.
        '''
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            shutil.rmtree(path)
            os.makedirs(path)