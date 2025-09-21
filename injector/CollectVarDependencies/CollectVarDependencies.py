import ast
from injector.helper import getEmptyRootNode


class CollectVarDependencies():
    '''
        Given a statement, this class will extract 
        all the variables and the dependencies. 

        TODO: Currently, there isn't support for tuple assignments
        where for example: (a,b) = (c,d). This will result in 
        vars = [a,b] and deps = [c,d] but this isn't correct.
    '''
    def __init__(self, node):
        self.vars = []
        self.deps = []
        self.visitedNodes = []

        node = getEmptyRootNode(node) if 'body' in node._fields else node
        self.processStatement(node)

    def doesVarExist(self, type, name, keys):
        '''
            Checks if a variable/dependency already exists.
        '''
        arr = self.deps if type == 'dep' else self.vars
        for item in arr:
            if item["name"] == name and item["keys"] == keys:
                item["count"] += 1
                return True
        return False

    def saveVarInfo(self, node, name, keys, isFunc=False):
        '''
            Saves the variabe info.

            Format:
            [Var Name, Var Keys, Number of times accessed or assigned]
        '''
        if isinstance(node.ctx, ast.Store):
            if not self.doesVarExist('var', name, keys):
                self.vars.append({
                    "name": name,
                    "keys": keys,
                    "isFunc": isFunc,
                    "count": 1
                })
        elif isinstance(node.ctx, ast.Load):
            if not self.doesVarExist('dep', name, keys):
                self.deps.append({
                    "name": name,
                    "keys": keys,
                    "isFunc": isFunc,
                    "count": 1
                })


    def processStatement(self, node):
        '''
            Walks through the given node and extracts 
            the keys for the variables that were accessed.

            If a node has already been visited, then skip
            the node.
        '''
        for node in ast.walk(node):

            if (node in self.visitedNodes):
                continue

            if isinstance(node, ast.Attribute):
                [name, keys, isFunc] = self.extractKeys(node)
                self.saveVarInfo(node, name, keys, isFunc)

            elif isinstance(node, ast.Subscript):
                [name, keys, isFunc] = self.extractKeys(node)
                self.saveVarInfo(node, name, keys, isFunc)

            elif isinstance(node, ast.Name):
                [name, keys, isFunc] = self.extractKeys(node)
                self.saveVarInfo(node, name, keys, isFunc)


    def extractKeys(self, node):
        '''
            Given a node, this function returns the keys
            used to access the variable value. 

            For example:
            a.b.c["key"] 

            results in

            ["a", ["b","c","key"]]

            Where a is the variable name and b,c,key are they
            keys used to access the variable value.
        '''
        keys = []
        while True:
            self.visitedNodes.append(node)
            if isinstance(node, ast.Attribute):
                keys.insert(0, node.attr)
                node = node.value
            elif isinstance(node, ast.Subscript):
                key = self.getSubscriptKey(node.slice)
                keys.insert(0, key)
                node = node.value
            elif isinstance(node, ast.Name):
                return node.id, keys, False
            elif isinstance(node, ast.Call):
                return node.func.id, keys, True
            else:
                return None, [], False

    def getSubscriptKey(self, slice_node):
        '''
            Gets the key of the subscript node.

            TODO: Currently, if the key is not a constant or name,
            it will unparse the code and return that as the key.
            This needs to be extended to add support for keys that
            are statements.
        '''
        if isinstance(slice_node, ast.Constant):
            return slice_node.value
        elif isinstance(slice_node, ast.Name):
            return slice_node.id
        elif hasattr(ast, 'unparse'):
            return ast.unparse(slice_node)
        return None