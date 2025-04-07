import logging
import json
import uuid

logger = logging.getLogger(__name__)

def varLog(val, varid):
    ''' 
       Returns a funtion used to log values based on their type as an AST node
       containing the aspAdliVarLog function definition.
       
       The aspAdliVarLog function logs values with special handling for objects:
       - For objects with __dict__, it logs their dictionary representation
       - For other values, it logs their string representation
       
       Returns:
          ast.Module: AST node containing the aspAdliVarLog function definition
    '''
    isDict = isinstance(val, dict)

    if (isDict):
        if "asp_uid" not in val:
            val = {"asp_uid": str(uuid.uuid4()), "asp_value": val}
    else:
        val = {"asp_uid": str(uuid.uuid4()), "asp_value": val}
    
    try:
        jsonVal = json.dumps(val, default=lambda o: o.__dict__ )
        logger.info(f"# {varid} {jsonVal}")
    except:
        logger.info(f"# {varid} {val}")

    return val