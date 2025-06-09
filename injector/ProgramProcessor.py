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


    def mapInjectedSourceLineno(self, tree):
        '''
            This function maps the lineno from the original
            source to the injected source.
        '''
        # Save the position of the original code 
        mapped = {}
        for count, node in enumerate(ast.walk(tree)):
            if hasattr(node, "logTypeCount") and hasattr(node, "lineno"):
                mapped[str(count)] = node.logTypeCount

        # Reparse the nodes so that the line metadata is updated
        parsed = ast.unparse(tree)
        tree = ast.parse(parsed)

        # Save the line number in log injected source to the log type map
        for count, node in enumerate(ast.walk(tree)):
            if str(count) in mapped and hasattr(node, "lineno"):
                ltInfo = self.ltMap[mapped[str(count)]]
                ltInfo["injectedLineno"] = node.lineno

    def run(self):
        '''
            Runs the injector.
        '''
        self.ltMap = {}
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
            injector = LogInjector(currAst, self.ltMap, logTypeCount, currRelPath)

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

        # Add AdliLogger.py to output directory
        source = getLoggerInstance()
        with open(Path(self.outputDirectory) / "AdliLogger.py", "w+") as f:
            f.write(source)        

        # Write files to output folder
        for fileInfo in fileOutputInfo:   
            if (fileInfo["currFilePath"] == self.sourceFile):
                currAst = helper.injectRootLoggingSetup(fileInfo["ast"], self.fileName)
            else:
                currAst = helper.injectLoggingSetup(fileInfo["ast"])

            # Map the line number in the original source to the line number in the injected source
            self.mapInjectedSourceLineno(currAst)

            with open(fileInfo["outputFilePath"], 'w+') as f:
                f.write(ast.unparse(currAst))
        
        # Save header to output folder
        header = {
            "fileTree": fileTree,
            "ltMap": self.ltMap,
            "varMap": varMap,
            "programInfo": programMetadata,
            "sysInfo": self.sysinfo,
            "adliInfo": self.adliInfo,
        }

        try:
            header_path = os.path.join(self.outputDirectory, "header.json")
            with open(header_path, "w+") as f:
                f.write(json.dumps(header, indent=2))
        except IOError as e:
            raise RuntimeError(f"Failed to write header.json: {e}")