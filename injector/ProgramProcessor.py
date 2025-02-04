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
        '''
            Process the program and inject diagnostic logs.
        '''
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
            injector = LogInjector(currAst, ltMap)

            fileTree[currRelPath] = {
                "source": source,
                "minLt": injector.minLtCount,
                "maxLt": injector.maxLtCount
            }

            fileOutputInfo.append({
                "outputFilePath": outputFilePath,
                "currFilePath": currFilePath,
                "ast": currAst                
            })

            self.writeInjectedTreesToFile(fileOutputInfo, fileTree, ltMap)

    def writeInjectedTreesToFile(self, fileOutputInfo, fileTree, ltMap):
        '''
            Injectes logging setup + fileTree and writes injected trees to file.
        '''
        for file in fileOutputInfo:     
            if (file["currFilePath"] == self.sourceFile):
                header = {
                    "fileTree": fileTree,
                    "ltMap": ltMap
                }
                currAst = helper.injectRootLoggingSetup(file["ast"], header, self.fileName)
            else:
                currAst = helper.injectLoggingSetup(file["ast"])

            with open(file["outputFilePath"], 'w+') as f:
                f.write(ast.unparse(currAst))

        with open("ltmap.json","w+") as f:
            f.write(json.dumps(ltMap))
    
    def clearAndCreateFolder (self, path):
        '''
            If folder exists, clear it and create it again.
        '''
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            shutil.rmtree(path)
            os.makedirs(path)