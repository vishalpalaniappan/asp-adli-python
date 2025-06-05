import ast

class CollectVarDependencies(ast.NodeVisitor):
    def __init__(self, node):
        self.var_dependencies = {}
        self.generic_visit(node)

    def visit_Assign(self, node):
        '''
            Collect variables and depdencies for assign statement.
        '''
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                deps = self._collect_dependencies(node.value)
                self.var_dependencies[var_name] = deps
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        '''
            Collect variable and dependencies for aug assign statement.
        '''
        if isinstance(node.target, ast.Name):
            var_name = node.target.id
            deps = self._collect_dependencies(node.value)
            deps.add(var_name)
            self.var_dependencies[var_name] = deps
        self.generic_visit(node)

    def _collect_dependencies(self, value):
        '''
            Collect all the variables that are loaded.
        '''
        deps = set()
        for node in ast.walk(value):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                deps.add(node.id)
        return deps

if __name__ == "__main__":
    n = ast.parse(
        '''
for i in [1,2,3,4]:
    b = p + c
        '''
    )
    a = CollectVarDependencies(n)
    print(a.var_dependencies)
