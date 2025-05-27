import logging
from pathlib import Path
from functools import wraps
from clp_logging.handlers import ClpKeyValuePairStreamHandler

import traceback
import threading
import json
import time
import os
import uuid
import contextvars
import asyncio

ADLI_EXECUTION_ID = str(uuid.uuid4())

path = Path(os.path.dirname(__file__)) / f"{ADLI_EXECUTION_ID}.clp.zst"
clp_handler = ClpKeyValuePairStreamHandler(open(path, "wb"))
logger = logging.getLogger("adli")
logger.setLevel(logging.INFO)
logger.addHandler(clp_handler)

coroutine_id = contextvars.ContextVar("coroutine_id", default=None) 

def track_coroutine(fn):
    '''
        This function wraps coroutines using a decorator and assigns
        a UID to each coroutine. When a coroutine makes a function call,
        the uid is preserved in the function that is called, allowing
        us to chain function calls made by coroutines.
    '''
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        token = None
        if coroutine_id.get() is None:
            uid = str(uuid.uuid4())
            token = coroutine_id.set(uid)
        try:
            return await fn(*args, **kwargs)
        finally:
            if token:
                coroutine_id.reset(token)
    return wrapper

def getTaskId():
    '''
        This function returns the name of the task that is
        currently being executed (if there is one).
    '''
    try:
        asyncio.get_running_loop()
        current_task = asyncio.current_task()
        return current_task.get_name() if current_task else None
    except RuntimeError:
        return None

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

    def processLevel(self, o, k, depth, max_depth):
        if isinstance(o, (str, int, float, bool)) or o is None:
            return o
        
        # TODO: Improve identifying circular references so we can remove max depth check.
        # obj_id = id(o)
        # if obj_id in self.visited:
        #     return "<Circular Reference Detected>"
        # self.visited.add(obj_id)

        if depth > max_depth:
            return '<Max Depth Reached>'
        
        if isinstance(o, dict):
            return {str(k): self.processLevel(v, str(k), depth + 1, max_depth) for (k, v) in o.items()}
        elif isinstance(o, (list, tuple, set)):
            return [self.processLevel(item, str(k), depth + 1, max_depth) for item in o]
        elif hasattr(o, '__dict__'):
            return {k: self.processLevel(v, str(k), depth + 1, max_depth) for (k, v) in vars(o).items()}
        else:
            return str(o)

    def variableToJson(self, obj, max_depth=8):
        self.visited = set()
        return self.processLevel(obj, "", 0, max_depth)

    def logVariable(self, varid, value):
        '''
            Logs the given varid and value. It also checks to see if the variable
            value was encoded by the ADLI tool and returns the decoded variable value.

            :param int varid: A number representing the mapped variable index in varMap.   
            :param value: Value of the variable being encoded.
        '''
        self.count += 1
        self.variableLogCount += 1

        try:
            # Try to serialize the variable
            adliValue = self.variableToJson(value)
            varObj = {
                "type": "adli_variable",
                "varid": varid,
                "thread": threading.get_ident(),
                "coroutine": coroutine_id.get(),
                "task": getTaskId(),
                "value": adliValue
            }
            logger.info(varObj)
        except Exception as e:
            # Fallback to string if serialization fails.
            varObj = {
                "type": "adli_variable",
                "varid": varid,
                "thread": threading.get_ident(),
                "coroutine": coroutine_id.get(),
                "task": getTaskId(),
                "value": str(value),
                "serialization_error": str(e)
            }
            logger.info(varObj)

        return self.decodeInput(value)

    def logStmt(self, stmtId):
        '''
            Logs the statement id. This corresponds to a statement in the source
            code. For example: a = 1 can be mapped to stmtId 4.

            :param int stmtId: A number representing the mapped statement index in ltMap.
        '''
        self.count += 1
        self.stmtLogCount += 1
        stmtObj = {
            "type": "adli_execution",
            "thread": threading.get_ident(),
            "coroutine": coroutine_id.get(),
            "task": getTaskId(),
            "value": stmtId
        }
        logger.info(stmtObj)

    def logException(self):
        '''
            Logs the exception using the traceback.
        '''
        self.count += 1
        self.exceptionLogCount += 1
        exceptionObj = {
            "type": "adli_exception",
            "thread": threading.get_ident(),
            "coroutine": coroutine_id.get(),
            "task": getTaskId(),
            "value": traceback.format_exc()
        }
        logger.info(exceptionObj)

    def logHeader(self, header):
        '''
            Log the header of the CDL file.

            :param dict header: Dictionary representing the header of the CDL file.
        '''
        self.count += 1

        # Add execution information to header
        header["execInfo"] = {
            "programExecutionId": ADLI_EXECUTION_ID,
            "timestamp": str(time.time()),
        }

        # TODO: Debug why logging the header directly causes
        # an error.
        logInfo = {
            "type": "adli_header",
            "thread": threading.get_ident(),
            "coroutine": coroutine_id.get(),
            "task": getTaskId(),
            "header": json.dumps(header)
        }
        logger.info(logInfo)

    def encodeOutput(self, variableName, value):
        '''
            Encodes the output with the execution id and position.

            :param str variableName: Name of the variable being encoded.
            :param value: Value of the variable being encoded.
        '''
        self.count += 1
        self.outputCount += 1

        logInfo = {
            "type": "adli_output",
            "outputName": variableName,
            "thread": threading.get_ident(),
            "coroutine": coroutine_id.get(),
            "task": getTaskId(),
            "adliExecutionId": ADLI_EXECUTION_ID,
            "adliExecutionIndex": self.count + 1,
            "adliValue": value
        }
        
        logger.info(logInfo)

        return {
            "adliExecutionId": ADLI_EXECUTION_ID,
            "adliExecutionIndex": self.count + 1,
            "adliValue": value
        }
    
    def decodeInput(self, value):
        '''
            This function identifies if the variable value is an encoded input.
            - If it is, log the input metadata and return the raw value of the variable. 
            - If it isn't, it returns the value.

            :param value: Value of the variable being inspected. 
        '''
        if isinstance(value, dict) and "adliExecutionId" in value and "adliExecutionIndex" in value:
            self.count += 1
            self.inputCount += 1

            logInfo = {
                "type": "adli_input",
                "thread": threading.get_ident(),
                "coroutine": coroutine_id.get(),
                "task": getTaskId(),
                "adliExecutionId": value["adliExecutionId"],
                "adliExecutionIndex": value["adliExecutionIndex"],
                "adliValue": value["adliValue"]
            }

            logger.info(logInfo)

            return value["adliValue"]
        
        return value


adli = AdliLogger()