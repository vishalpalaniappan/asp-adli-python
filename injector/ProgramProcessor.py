import shutil
import os
import ast
import json
from pathlib import Path
from injector import helper
from injector.FindLocalImports import findLocalImports
from injector.LogInjector import LogInjector

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
        ltMap = {}
        fileTree = {}
        fileOutputInfo = []
        files = findLocalImports(self.sourceFile)

        # Process every file found in the program
        for currFilePath in files:
            currRelPath = os.path.relpath(currFilePath, self.sourceFileDirectory)
            outputFilePath = os.path.join(self.outputDirectory, currRelPath)
            outputFileDir = os.path.dirname(outputFilePath)

            if (not os.path.exists(outputFileDir)):
                os.makedirs(outputFileDir)

            with open(currFilePath, "r") as f:
                source = f.read()

            currAst = ast.parse(source)
            fileTree[currRelPath] = source
            LogInjector(currAst, ltMap)

            fileOutputInfo.append({
                "outputFilePath": outputFilePath,
                "currFilePath": currFilePath,
                "ast": currAst                
            })

        #Inject ltMap, fileTree and logging setup and write to output file.
        for file in fileOutputInfo:     
            if (file["currFilePath"] == self.sourceFile):
                currAst = self.injectRootLoggingSetup(file["ast"], ltMap, fileTree)
            else:
                currAst = self.injectLoggingSetup(file["ast"])

            with open(file["outputFilePath"], 'w+') as f:
                f.write(ast.unparse(currAst))

        with open("ltmap.json","w+") as f:
            f.write(json.dumps(ltMap))


    def injectRootLoggingSetup(self, tree, ltMap, fileTree):
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
        
        return ast.Module( body=[
            helper.getRootLoggingSetup(self.fileName).body,
            helper.getLoggingFunction().body,
            helper.getLoggingStatement(json.dumps(ltMap)),
            helper.getLoggingStatement(json.dumps(fileTree)),
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