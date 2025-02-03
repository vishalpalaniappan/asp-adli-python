import shutil
import os
import ast
from pathlib import Path
from injector import helper
from injector.FindLocalImports import findLocalImports
from injector.LogInjectorVisitor import LogInjectorVisitor

class ProgramProcessor:
    '''
        This class accepts a source file and processes it and any local
        imports found using the log injector. It then writes the injected
        source files to the output directory.
    '''

    def __init__(self, sourceFile, workingDirectory):
        self.sourceFile = os.path.abspath(sourceFile)
        self.fileName = Path(self.sourceFile).stem
        self.sourceFileDirectory = os.path.dirname(sourceFile)
        self.outputDirectory = os.path.join(workingDirectory, "output")
        self.clearAndCreateFolder(self.outputDirectory)

    def run(self):

        for currFilePath in findLocalImports(self.sourceFile):
            # Create output file path and output file directory
            currRelPath = os.path.relpath(currFilePath, self.sourceFileDirectory)
            outputFilePath = os.path.join(self.outputDirectory, currRelPath)
            outputFileDir = os.path.dirname(outputFilePath)

            # Create directory if it doesn't exist
            if (not os.path.exists(outputFileDir)):
                os.makedirs(outputFileDir)

            # Read the current file and parse into AST
            with open(currFilePath, "r") as f:
                currAst = ast.parse(f.read())
            
            # Inject adli specific nodes into source file
            if (currFilePath == self.sourceFile):
                currAst = self.injectRootLoggingSetup(currAst)
            else:
                currAst = self.injectLoggingSetup(currAst)

            # Write injected source into output directory
            with open(outputFilePath, 'w+') as f:
                f.write(ast.unparse(currAst))


    def injectRootLoggingSetup(self, tree):
        '''
            Injects try except structure around the given tree.
            Injects root logging setup and function the given tree.
        '''
        mainTry = ast.Try(
            body=tree.body,
            handlers=[helper.getExceptionLog()],
            orelse=[],
            finalbody=[]
        )
        loggingSetup = helper.getRootLoggingSetup(self.fileName)
        loggingFunction = helper.getLoggingFunction()
        
        return ast.Module( body=[
            loggingSetup.body,
            loggingFunction.body,
            mainTry.body
        ], type_ignores=[])

    def injectLoggingSetup(self, tree):
        '''
            Injects logging setup and function into the provided tree.
        '''
        loggingSetup = helper.getLoggingSetup()
        loggingFunction = helper.getLoggingFunction()
        return ast.Module( body=[
            loggingSetup.body,
            loggingFunction.body,
            tree.body
        ], type_ignores=[])
    
    def clearAndCreateFolder (self, path):
        '''
            If folder exists, clear it and create it again.
        '''
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            shutil.rmtree(path)
            os.makedirs(path)