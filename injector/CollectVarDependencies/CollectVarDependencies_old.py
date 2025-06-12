import ast
import json

class CollectVarDependencies(ast.NodeVisitor):
    def __init__(self):
        self.targets = []
        self.dependencies = []

    def extractKeys(self, node):
        '''
            Starting at a attribute, name or subscript,
            walk until a name node is found.

            a.b.c[2]["test"]
        
        '''
        keys = []
        nodesToVisit = []
        variable = {}

        for _node in ast.walk(node):

            if isinstance(_node, ast.Attribute):
                keys.append({"type": "key", "value": _node.attr})

            elif isinstance(_node, ast.Subscript):
                print(ast.unparse(_node))
                if isinstance(_node.slice, ast.Constant):
                    keys.append({"type": "constant", "value": _node.slice.value})
                elif isinstance(_node.slice, ast.Name):
                    keys.append({"type": "variable", "value": _node.slice.id})
                else:
                    nodesToVisit.append(node.slice)

            elif isinstance(_node, ast.Name):
                variable["name"] = _node.id
                variable["keys"] = keys
                if isinstance(node.ctx, ast.Store):
                    self.targets.append(variable)
                elif isinstance(node.ctx, ast.Load):
                    self.dependencies.append(variable)
                break
    
        return nodesToVisit

    def visit_Name(self, node):
        self.extractKeys(node)

    def visit_Subscript(self, node):
        nodesToVisit = self.extractKeys(node)

        for _node in nodesToVisit:
            self.generic_visit(_node)

    def visit_Attribute(self, node):
        self.extractKeys(node)



if __name__ == "__main__":
    n = ast.parse("b.c['12'] = m + d[a] + e.p[a.b + 2] + somefunc(2 + p.b[2] + a.b.c[2]['test'][k.l])")
    n = ast.parse("b.c['12'] = a.b.c[2]['test'][x.y]")
    # n = ast.parse("vself.nodeVarInfo += CollectCallVariables(node, self.logTypeCount, self.funcId, self.varMap).variables")
    d = CollectVarDependencies()
    d.visit(n.body[0])

    for t in d.targets:
        print(t)

    for d in d.dependencies:
        print(d)
    # print(json.dumps(d.targets, indent=4))

    # print(json.dumps(d.dependencies, indent=4))


    # walk_ast(n.body[0])