import logging
from pathlib import Path
from clp_logging.handlers import CLPFileHandler

import traceback
import json
import time
import os
import uuid

ADLI_EXECUTION_ID = str(uuid.uuid4())

path = Path(os.path.dirname(__file__)) / f"{ADLI_EXECUTION_ID}.clp.zst"
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
        self.variableLogCount = 0
        self.stmtLogCount = 0
        self.exceptionLogCount = 0
        self.inputCount = 0
        self.outputCount = 0
        pass

    def logVariable(self, varid, value):
        '''
            Logs the given varid and value.         
        '''
        self.count += 1
        self.variableLogCount += 1
        try:
            dumpedValue = json.dumps(value, default=lambda o: o.__dict__ )
            logger.info(f"# {varid} {dumpedValue}")
        except:
            logger.info(f"# {varid} {value}")

        return self.decodeInput(value)

    def logStmt(self, stmtId):
        '''
            Logs the mapped stmtId.
        '''
        self.count += 1
        self.stmtLogCount += 1
        logger.info(stmtId)

    def logException(self):
        '''
            Logs the exception using the traceback.
        '''
        self.count += 1
        self.exceptionLogCount += 1
        logger.error(f"? {traceback.format_exc()}")

    def logHeader(self, header):
        '''
            Logs the header, 
        '''
        self.count += 1
        header["execInfo"] = {
            "programExecutionId": ADLI_EXECUTION_ID,
            "timestamp": str(time.time()),
        }
        logger.info(json.dumps(header))

    def encodeOutput(self, variableName, value):
        '''
            Encodes the output with the execution id and position.
        '''
        self.count += 1
        self.outputCount += 1
        logger.info(f"* output {ADLI_EXECUTION_ID} {self.count + 1}")
        return {
            "adliExecutionId": ADLI_EXECUTION_ID,
            "adliPosition": self.count + 1,
            "adliValue": value
        }
    
    def decodeInput(self, value):
        if isinstance(value, dict) and "adliExecutionId" in value and "adliPosition" in value:
            self.count += 1
            self.inputCount += 1
            logger.info(f"* input {value['adliExecutionId']} {value['adliPosition']}")
            return value["adliValue"]
        
        return value


adli = AdliLogger()