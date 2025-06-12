import ast

class CollectVarDependencies():
    def __init__(self, node):
        self.vars = []
        self.deps = []
        self.visitedNodes = []

        self.processStatement(node)

        print(self.vars)
        print(self.deps)


    def saveVarInfo(self, node, name, keys):
        if isinstance(node.ctx, ast.Store):
            self.vars.append([name, keys])
        elif isinstance(node.ctx, ast.Load):
            self.deps.append([name, keys])


    def processStatement(self, node):
        for node in ast.walk(node):

            if (node in self.visitedNodes):
                continue

            if isinstance(node, ast.Attribute):
                [name, keys] = self._extract_access_path(node)
                self.saveVarInfo(node, name, keys)

            elif isinstance(node, ast.Subscript):
                [name, keys] = self._extract_access_path(node)
                self.saveVarInfo(node, name, keys)

            elif isinstance(node, ast.Name):
                [name, keys] = self._extract_access_path(node)
                self.saveVarInfo(node, name, keys)


    def _extract_access_path(self, node):
        keys = []
        while True:
            self.visitedNodes.append(node)
            if isinstance(node, ast.Attribute):
                keys.insert(0, node.attr)
                node = node.value
            elif isinstance(node, ast.Subscript):
                key = self._get_subscript_key(node.slice)
                keys.insert(0, key)
                node = node.value
            elif isinstance(node, ast.Name):
                return node.id, keys
            else:
                return None, []

    def _get_subscript_key(self, slice_node):
        if isinstance(slice_node, ast.Constant):
            return slice_node.value
        elif isinstance(slice_node, ast.Name):
            return slice_node.id
        elif hasattr(ast, 'unparse'):
            return ast.unparse(slice_node)
        return None



if __name__ == "__main__":
    # n = ast.parse("b.c['12'] = m + d[a] + e.p[a.b + 2] + somefunc(2 + p.b[2] + a.b.c[2]['test'][k.l])")
    n = ast.parse("b.c['12'] = a.b.c[2]['test'][k.l]")
    # n = ast.parse("b.c = 21")
    # n = ast.parse("vself.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables")

    CollectVarDependencies(n)