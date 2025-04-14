import shutil
import os
import ast
import uuid
import json
import time
from pathlib import Path
from injector import helper
from injector.FindLocalImports import findLocalImports
from injector.LogInjector import LogInjector
from injector.LoggerInstance.getLoggerInstance import getLoggerInstance

SAVE_HEADER = True

class ProgramProcessor:
    '''
        This class accepts a source file and processes it and any local
        imports found using the log injector. It then writes the injected
        source files to the output directory.
    '''
    def __init__(self, sourceFile, workingDirectory, sysinfo):
        self.sourceFile = os.path.abspath(sourceFile)
        self.fileName = Path(self.sourceFile).stem
        self.sourceFileDirectory = os.path.dirname(self.sourceFile)                
        self.outputDirectory = os.path.join(workingDirectory, "output", self.fileName)

        self.sysinfo = sysinfo
        # Create header object
        self.adliInfo = {
            "adliExecutionId": str(uuid.uuid4()),
            "timestamp": str(time.time())
        }

        if os.path.exists(self.outputDirectory):
            shutil.rmtree(self.outputDirectory)
        os.makedirs(self.outputDirectory)

    def run(self):
        '''
            Runs the injector.
        '''
        ltMap = {}
        varMap = {}
        fileTree = {}
        fileOutputInfo = []
        files = findLocalImports(self.sourceFile)
        logTypeCount = 0
        programMetadata = {}

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

            if(injector.metadata):
                programMetadata = injector.metadata

            logTypeCount = injector.logTypeCount

            for key in injector.varMap:
                varMap[key] = injector.varMap[key]

            fileTree[currRelPath] = {
                "source": source,
                "minLt": injector.minLogTypeCount,
                "maxLt": injector.maxLogTypeCount
            }

            fileOutputInfo.append({
                "outputFilePath": outputFilePath,
                "currFilePath": currFilePath,
                "ast": currAst                
            })

        
        header = {
            "fileTree": fileTree,
            "ltMap": ltMap,
            "varMap": varMap,
            "programInfo": programMetadata,
            "sysInfo": self.sysinfo,
            "adliInfo": self.adliInfo
        }

        # Add AdliLogger.py to output directory
        source = getLoggerInstance()
        with open(Path(self.outputDirectory) / "AdliLogger.py", "w+") as f:
            f.write(source)
        

        # Write files to output folder
        for fileInfo in fileOutputInfo:   
            if (fileInfo["currFilePath"] == self.sourceFile):
                currAst = helper.injectRootLoggingSetup(fileInfo["ast"], header, self.fileName)
            else:
                currAst = helper.injectLoggingSetup(fileInfo["ast"])

            with open(fileInfo["outputFilePath"], 'w+') as f:
                f.write(ast.unparse(currAst))

        if SAVE_HEADER:
            with open(os.path.join(self.outputDirectory, "header.json"), "w+") as f:
                f.write(json.dumps(header))