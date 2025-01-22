
from injector import LogInjector

class ProgramProcessor:

    def __init__(self, sourceFile):
        self.sourceFile = sourceFile
        pass

    def run(self):
        """Process the source file for diagnostic log injection.
        - Creates a queue to process all files in the program. 
        - Creates a LogInjector instance for each file in the program. 
        - Adds any local imports found to the queue and continues processing.

        Args:
            sourceFile: Path to the source file to be processed
        """
        inj = LogInjector.LogInjector(self.sourceFile, 0)
        inj.run()