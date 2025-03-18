import ast
import uuid

class VariableCollectorBase:
    '''
        Base class for collecting var info and generation var info object.
    '''
    var_count = 0
    
    def __init__(self, logTypeId, funcId):
        self.variables = []
        self.logTypeId = logTypeId
        self.funcId = funcId
    
    def getVarInfo(self, name, keys, syntax, node):
        '''
            Appends varinfo object to the variables list.
        '''
        VariableCollectorBase.var_count += 1
        self.variables.append({
            "varId": VariableCollectorBase.var_count,
            "name": name,
            "keys": keys,
            "syntax": syntax,
            "assignValue": node,
            "logType": self.logTypeId,
            "funcId": self.funcId,
            "isTemp": node is not None
        })