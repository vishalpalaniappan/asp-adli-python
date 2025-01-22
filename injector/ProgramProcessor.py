from injector import helper
import json
import ast
import os
from injector.LogInjector import LogInjector

class ProgramProcessor:

    def __init__(self, sourceFile):
        self.sourceFile = sourceFile
        self.sourceDir = os.path.dirname(sourceFile)
        self.fileTree = {}
        pass


    def getInjectedSourceRoot(self, inj):
        '''
            Given an injector object, this funtion returns 
            a program injected with diagnostic logs.
        '''
        loggingSetupNodes = helper.getRootLoggingSetup("test")
        fileTreeNodes = [
            helper.getLoggingStatement(json.dumps(self.fileTree))
        ]
        injectedSourceNodes = inj.injectedTree.body

        injectedNodes = loggingSetupNodes.body + fileTreeNodes + injectedSourceNodes
        return ast.unparse(injectedNodes)

    def run(self):
        ltCount = 0
        inj = LogInjector(self.sourceDir, self.sourceFile, ltCount)
        inj.run()

        self.fileTree[self.sourceFile] = {
            "source": inj.source,
            "sst": inj.sst.tree
        }

        injectedSource = self.getInjectedSourceRoot(inj)

        with open("test.py","w+") as f:
            f.write(injectedSource)