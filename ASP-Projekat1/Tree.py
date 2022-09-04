"""
Modul sadrži implementaciju stabla.
"""
#izvorni kod sa enastave


class TreeNode(object):
    __slots__ = 'parent', 'children', 'position'

    def __init__(self, position):
        self.parent = None
        self.children = []
        self.position = position

    def is_root(self):
        return self.parent is None

    def is_leaf(self):
        return len(self.children) == 0

    def add_child(self, node):
        node.parent = self
        self.children.append(node)


class Tree(object):
    def __init__(self):
        self.root = None

    def is_empty(self):
        return self.root is None

    def depth(self, node):
        if node.is_root():
            return 0
        else:
            return 1 + self.depth(node.parent)

    def _height(self, node):
        if node.is_leaf():
            return 0
        else:
            return 1 + max(self._height(child) for child in node.children)

    def height(self):
        return self._height(self.root)


if __name__ == '__main__':
    # instanca stabla
    t = Tree()
    broj = 5
    d = TreeNode(broj)
    t.root = d
    k = TreeNode(10)

    # kreiranje relacija između novih čvorova
    a = TreeNode(1)
    b = TreeNode(2)
    c = TreeNode(3)
    d.add_child(a)
    a.add_child(b)
    t.root = a
    broj = 86

    print(d.position)


