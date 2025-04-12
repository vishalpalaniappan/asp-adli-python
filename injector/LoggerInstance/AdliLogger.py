import logging
from pathlib import Path
from clp_logging.handlers import CLPFileHandler

import traceback
import json
import time
import os

ADLI_UNIQUE_ID = str(int(time.time()))

path = Path(os.path.dirname(__file__)) / f"./{ADLI_UNIQUE_ID}.clp.zst"
clp_handler = CLPFileHandler(path)
logger = logging.getLogger("adli")
logger.setLevel(logging.INFO)
logger.addHandler(clp_handler)

class AdliLogger:
    '''
        This class holds all the logging functions used by the ADLI 
        tool during runtime. It maintains a count of the number of 
        logged executions so that each logged instruction can be 
        uniquely identified.
    '''

    def __init__(self):
        self.count = 0
        self.variableLog = 0
        self.stmtLog = 0
        self.exceptionLog = 0
        pass

    def logVariable(self, varid, value):
        '''
            Logs the given varid and value.         
        '''
        self.count += 1
        self.variableLog += 1
        try:
            value = json.dumps(value, default=lambda o: o.__dict__ )
            logger.info(f"# {varid} {value}")
        except:
            logger.info(f"# {varid} {value}")

    def logStmt(self, stmtId):
        '''
            Logs the mapped stmtId.
        '''
        self.count += 1
        self.stmtLog += 1
        logger.info(stmtId)

    def logException(self):
        '''
            Logs the exception using the traceback.
        '''
        self.count += 1
        self.exceptionLog += 1
        logger.error(traceback.format_exc())

    def logHeader(self, header):
        '''
            Logs the header, 
        '''
        self.count += 1
        logger.info(header)

    def encodeOutput(self, variable):
        '''
            This function will encode any output with the uniqueid
            of this log file and the current execution position.
        '''
        pass

    def decodeInput(self, variable):
        pass


adli = AdliLogger()