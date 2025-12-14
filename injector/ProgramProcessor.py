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
from injector.LoadDesignConfiguration import getDesignFile, getAbsMapFile, getSdgFile, getSdgMetaFile

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
        files = findLocalImports(self.sourceFile)
        logTypeCount = 0
        programMetadata = {}
        sdg = getSdgFile(self.sourceFile)
        sdg_meta = getSdgMetaFile(self.sourceFile)
        abs_map = getAbsMapFile(self.sourceFile)
        design_map = getDesignFile(self.sourceFile)

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
            injector = LogInjector(source, currAst, logTypeCount, currRelPath, isRoot, abs_map)

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
            "adliInfo": self.adliInfo
        }

        # Only include design file keys if valid files were provided.
        if (sdg):
            header["sdg"] = sdg

        if (sdg_meta):
            header["sdg_meta"] = sdg_meta

        if (design_map):
            header["design_map"] = design_map

        try:
            header_path = os.path.join(self.outputDirectory, "header.json")
            with open(header_path, "w+") as f:
                f.write(json.dumps(header, indent=2))
        except IOError as e:
            raise RuntimeError(f"Failed to write header.json: {e}")