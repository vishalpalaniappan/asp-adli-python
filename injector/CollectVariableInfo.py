import ast
import uuid
from injector.helper import getEmptyRootNode

class VariableCollectorBase:
    '''
        Base class for collecting var info and generation var info object.
    '''
    var_count = 0
    temp_var_count = 0
    
    def __init__(self, logTypeId, funcId):
        self.variables = []
        self.logTypeId = logTypeId
        self.funcId = funcId
        
    def getVariableName(self):
        '''
            Generates a remporary variable name using the uuid module. This
            variable will be hidden from the user in the diagnostic log viewer.
        '''
        VariableCollectorBase.var_count += 1
        return "asp_temp_var_" + str(VariableCollectorBase.var_count)
    
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

class CollectAssignVarInfo(ast.NodeVisitor, VariableCollectorBase):
    '''
        Collects variable info from assign node targets. It also 
        extracts the keys of the target node.
    '''

    def __init__(self, node, logTypeId, funcId):
        VariableCollectorBase.__init__(self, logTypeId, funcId)
        self.node = node
        self.keys = []
        self.containsSlice = False
        self.generic_visit(ast.Module(body=[node], type_ignores=[]))
        
        if self.containsSlice:
            '''
            There isn't support for creating keys from slice nodes.
            So for now, we remove the keys and log the whole variable. 
            There will be further support added for this in the future.
            '''
            name = self.keys.pop(0)["value"]
            self.getVarInfo(name, [], name, None)
        elif len(self.keys) > 0:
            name = self.keys.pop(0)["value"]
            self.getVarInfo(name, self.keys, ast.unparse(self.node), None)

    def visit_Subscript(self, node):
        '''
            If any of the subscript nodes are an expression that need 
            to be evaluated, then create a temporary variable and replace
            the subscript with the name of the temporary variable. 
        '''
        if isinstance(node.slice, (ast.Slice, ast.Tuple)):
            self.generic_visit(node)
            self.containsSlice = True

        elif not isinstance(node.slice, (ast.Constant, ast.Name)):
            self.generic_visit(ast.Module(body=[node.value], type_ignores=[]))

            varName = self.getVariableName()
            self.keys.append({"type": "temp_variable", "value": varName})
            self.getVarInfo(varName, [], varName, node.slice)

            node.slice = ast.Name(id= varName, ctx=ast.Load())
        else:
            self.generic_visit(node)
        return node
    
    def visit_Name(self, node):
        self.generic_visit(node)
        self.keys.append({"type":"variable", "value":node.id})
        return node
    
    def visit_Attribute(self, node):
        self.generic_visit(node)
        self.keys.append({"type":"key", "value":node.attr})
        return node
    
    def visit_Constant(self, node):
        self.generic_visit(node)
        self.keys.append({"type":"key", "value":node.value})
        return node
    

class CollectFunctionArgInfo(ast.NodeVisitor, VariableCollectorBase):
    '''
        Collects the variable info for arguments to the function. 
        TODO: Remove this class once the feature to extract the
        arguments from call location are implemented.
    '''

    def __init__(self, node, logTypeId, funcId):
        VariableCollectorBase.__init__(self, logTypeId, funcId)
        self.generic_visit(node)
    
    def visit_arg(self, node):
        self.getVarInfo(node.arg, [], node.arg, None)
        self.generic_visit(node)
    

class CollectVariableDefault(ast.NodeVisitor, VariableCollectorBase):
    '''
        This class collects any name nodes in the provided node. For
        nodes with a body, it removes the children before finding 
        the valid names. For example, in the case of a for loop,
        this would log the variable info for the current element in
        the loop.
    '''

    def __init__(self, node, logTypeId, funcId):
        VariableCollectorBase.__init__(self, logTypeId, funcId)

        if 'body' in node._fields:
            emptyNode = getEmptyRootNode(node)
            self.generic_visit(emptyNode)
        else:
            self.generic_visit(node)
    
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.getVarInfo(node.id, [], node.id, None)
        self.generic_visit(node)


        
    

class CollectCalls(ast.NodeVisitor, VariableCollectorBase):
    '''
        This class collects any name nodes in the provided node. For
        nodes with a body, it removes the children before finding 
        the valid names. For example, in the case of a for loop,
        this would log the variable info for the current element in
        the loop.
    '''

    def __init__(self, node, logTypeId, funcId):
        VariableCollectorBase.__init__(self, logTypeId, funcId)

        if 'body' in node._fields:
            emptyNode = getEmptyRootNode(node)
            self.generic_visit(emptyNode)
        else:
            self.generic_visit(node)
    
    def visit_Call(self, node):
        args = []
        for arg in node.args:
            if not isinstance(arg, (ast.Name)):
                varName = self.getVariableName()
                self.getVarInfo(varName, [], varName, arg)
                args.append(ast.Name(id= varName, ctx=ast.Load()))
            else:
                args.append(arg)

        node.args = args
        return node


    