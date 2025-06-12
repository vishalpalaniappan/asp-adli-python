import ast
import uuid
import json
import inspect

# from injector.VariableCollectors.BaseVariableCollector import VariableCollectorBase
# from VariableCollectors.BaseVariableCollector import VariableCollectorBase

class CollectVarDependencies(ast.NodeVisitor):
    # def __init__(self, node, logTypeId, funcId):
    def __init__(self, node):
        self.node = node
        self.visitedNodes = []
        self.keys = []
        self.name = None
        self.containsSlice = False

        if isinstance(node.ctx, ast.Store):
            self.type = "var"
        elif isinstance(node.ctx, ast.Load):
            self.type = "dep"

        self.generic_visit(ast.Module(body=[node], type_ignores=[]))
        if self.containsSlice:
            '''
            There isn't support for creating keys from slice nodes.
            So for now, we remove the keys and log the whole variable. 
            There will be further support added for this in the future.
            '''
            name = self.keys.pop(0)["value"]
        elif len(self.keys) > 0:
            name = self.keys.pop(0)["value"]
        
    def getVariableName(self):
        '''
            Generates a temporary variable name using the uuid module. This
            variable will be hidden from the user in the diagnostic log viewer.
        '''
        return "asp_temp_var_" + str(uuid.uuid1()).replace("-", "")

    def visit_Subscript(self, node):
        '''
            If any of the subscript nodes are an expression that need 
            to be evaluated, then create a temporary variable and replace
            the subscript with the name of the temporary variable. 
        '''
        self.visitedNodes.append(node)
        if isinstance(node.slice, (ast.Slice, ast.Tuple)):
            self.generic_visit(node)
            self.containsSlice = True
        else:
            self.generic_visit(node.value)
        return node
    
    def visit_Name(self, node):
        
        frame = inspect.currentframe().f_back
        print("")
        print(frame)
        code = inspect.getframeinfo(frame).code_context[0].strip()
        print("Call site:", code)

        self.visitedNodes.append(node)
        self.name = node.id
        # self.generic_visit(node)
        return node
    
    def visit_Attribute(self, node):
        self.visitedNodes.append(node)
        if isinstance(node.value, (ast.Constant, ast.Attribute, ast.Subscript,ast.Name)):
            self.generic_visit(node)
        return node
    
    def visit_Constant(self, node):
        self.visitedNodes.append(node)
        self.generic_visit(node)
        return node
    
if __name__ == "__main__":
    # n = ast.parse("b.c['12'] = m + d[a] + e.p[a.b + 2] + somefunc(2 + p.b[2] + a.b.c[2]['test'][k.l])")
    # n = ast.parse("b.c['12'] = a.b.c[2]['test'][k.l]")
    # n = ast.parse("b.c = 21")
    n = ast.parse("vself.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables")

    # d.visit(n.body[0])

    vars = set()
    deps = set()

    visitedNodes = []
    for node in ast.walk(n):

        if (node in visitedNodes):
            continue

        d = None
        if isinstance(node, ast.Attribute):
            d = CollectVarDependencies(node)
            visitedNodes += d.visitedNodes

        elif isinstance(node, ast.Subscript):
            d = CollectVarDependencies(node)
            visitedNodes += d.visitedNodes

        elif isinstance(node, ast.Name):
            d = CollectVarDependencies(node)
            visitedNodes += d.visitedNodes

        if d and d.name is not None:
            if d.type == "var":
                vars.add(d.name)
            elif d.type == "dep":
                deps.add(d.name)

    print(vars, deps)