import ast

class ASTFormer:
    def __init__(self, source):
        self.source = open(source,"r").read()
        self.tree = ast.parse(source)

    def dump(self):
        return ast.dump(self.tree)

