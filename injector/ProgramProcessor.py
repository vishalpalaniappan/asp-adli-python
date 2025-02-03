import shutil
import os
from injector.FindLocalImports import findLocalImports

class ProgramProcessor:
    '''
        This class accepts a source file and processes it and any local
        imports found using the log injector. It then writes the injected
        source files to the output directory.
    '''

    def __init__(self, sourceFile, workingDirectory):
        self.sourceFile = sourceFile
        self.sourceFileDirectory = os.path.dirname(sourceFile)
        self.outputDirectory = os.path.join(workingDirectory, "output")
        self.clearAndCreateFolder(self.outputDirectory)

    def run(self):

        filePaths = findLocalImports(self.sourceFile)

        for currFilePath in filePaths:
            # Create output file path and output file directory
            currRelPath = os.path.relpath(currFilePath, self.sourceFileDirectory)
            outputFilePath = os.path.join(self.outputDirectory, currRelPath)
            outputFileDir = os.path.dirname(outputFilePath)

            # Create directory if it doesn't exist
            if (not os.path.exists(outputFileDir)):
                os.makedirs(outputFileDir)

            with open(currFilePath, 'r') as f:
                source = f.read()

            with open(outputFilePath, 'w+') as f:
                f.write(source)
    
    def clearAndCreateFolder (self, path):
        '''
            If folder exists, clear it and create it again.
        '''
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            shutil.rmtree(path)
            os.makedirs(path)