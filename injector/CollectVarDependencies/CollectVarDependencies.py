import ast
from injector.helper import getEmptyRootNode

class CollectVarDependencies(ast.NodeVisitor):
    def __init__(self, node):
        self.var_dependencies = {}

        if 'body' in node._fields:
            emptyNode = getEmptyRootNode(node)
            self.generic_visit(ast.Module(body=[emptyNode], type_ignores=[]))
        else:
            self.generic_visit(ast.Module(body=[node], type_ignores=[]))

    def visit_Assign(self, node):
        '''
            Collect variables and depdencies for assign statement.
        '''
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                deps = self._collect_dependencies(node.value)
                if deps:
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
        deps = []
        for node in ast.walk(value):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                deps.append(node.id)
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
