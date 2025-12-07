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
        sdg = {}
        sdg_meta = {}
        #
        # Get the Semantic Design Graph (SDG)
        no_ext, _ = os.path.splitext(self.sourceFile)
        sdg_path = no_ext + "_sdg.json"

        try:
            with open(sdg_path, "r") as f:
                sdg = json.loads(f.read())
        except FileNotFoundError:
            print("Could not find SDG file for", self.sourceFile)
            sdg = {}
        except json.JSONDecodeError:
            print("SDG file is not a valid JSON for", self.sourceFile)
            sdg = {}
        
        # Get the Semantic Design Graph (SDG) meta file
        no_ext, _ = os.path.splitext(self.sourceFile)
        sdg_path = no_ext + "_meta.json"

        try:
            with open(sdg_path, "r") as f:
                sdg_meta = json.loads(f.read())
        except FileNotFoundError:
            print("Could not find SDG metadata file for", self.sourceFile)
            sdg = {}
        except json.JSONDecodeError:
            print("SDG metadata file is not a valid JSON for", self.sourceFile)
            sdg = {}

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
            isRoot = (self.sourceFile == currFilePath)
            injector = LogInjector(currAst, logTypeCount, currRelPath, isRoot)

            if(injector.metadata):
                programMetadata = injector.metadata

            logTypeCount = injector.logTypeCount

            for key in injector.varMap:
                varMap[key] = injector.varMap[key]

            for key in injector.ltMap:
                ltMap[key] = injector.ltMap[key]

            fileTree[currRelPath] = {
                "source": source,
                "minLt": injector.minLogTypeCount,
                "maxLt": injector.maxLogTypeCount
            }

            with open(outputFilePath, 'w+') as f:
                f.write(ast.unparse(injector.tree))

        # Add AdliLogger.py to output directory
        source = getLoggerInstance()
        with open(Path(self.outputDirectory) / "AdliLogger.py", "w+") as f:
            f.write(source)     
        
        # Save header to output folder
        header = {
            "fileTree": fileTree,
            "ltMap": ltMap,
            "varMap": varMap,
            "programInfo": programMetadata,
            "sysInfo": self.sysinfo,
            "adliInfo": self.adliInfo,
            "sdg": sdg,
            "sdg_meta": sdg_meta
        }

        try:
            header_path = os.path.join(self.outputDirectory, "header.json")
            with open(header_path, "w+") as f:
                f.write(json.dumps(header, indent=2))
        except IOError as e:
            raise RuntimeError(f"Failed to write header.json: {e}")