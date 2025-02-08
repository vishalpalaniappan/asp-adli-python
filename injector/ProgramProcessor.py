import shutil
import os
import ast
import json
from pathlib import Path
from injector import helper
from injector.FindLocalImports import findLocalImports
from injector.LogInjector import LogInjector

SAVE_LT_MAP = False

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

        if os.path.exists(self.outputDirectory):
            shutil.rmtree(self.outputDirectory)
        os.makedirs(self.outputDirectory)

    def run(self):
        '''
            Processes the program by doing the following:
            ----------------------------------------------
            1. Find all locally imported files in the program
            2. Inject logs into each source file
            3. Write injected log tree into output folder
        '''
        ltMap = {}
        fileTree = {}
        fileOutputInfo = []
        files = findLocalImports(self.sourceFile)
        logTypeCount = 0

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
            injector = LogInjector(currAst, ltMap, logTypeCount)

            logTypeCount = injector.maxLtCount

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

        # Write files to output folder
        for file in fileOutputInfo:     
            if (file["currFilePath"] == self.sourceFile):
                header = {"fileTree": fileTree, "ltMap": ltMap}
                currAst = helper.injectRootLoggingSetup(file["ast"], header, self.fileName)
            else:
                currAst = helper.injectLoggingSetup(file["ast"])

            with open(file["outputFilePath"], 'w+') as f:
                f.write(ast.unparse(currAst))

        if SAVE_LT_MAP:
            with open(os.path.join(self.outputDirectory, "ltMap.json"), "w+") as f:
                f.write(json.dumps(ltMap))