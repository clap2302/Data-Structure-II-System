class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t
        self.keys = []
        self.values = []
        self.children = []
        self.leaf = leaf

    def is_full(self):
        return len(self.keys) == (2 * self.t - 1)


class BTree:
    def __init__(self, t=2):
        self.root = BTreeNode(t, leaf=True)
        self.t = t

    def search(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and key == node.keys[i]:
            return node, i

        if node.leaf:
            return None

        return self.search(node.children[i], key)

    def split_child(self, parent, index, child):
        t = self.t
        new_child = BTreeNode(t, leaf=child.leaf)

        parent.keys.insert(index, child.keys[t - 1])
        parent.values.insert(index, child.values[t - 1])
        parent.children.insert(index + 1, new_child)

        new_child.keys = child.keys[t:]
        new_child.values = child.values[t:]

        child.keys = child.keys[:t - 1]
        child.values = child.values[:t - 1]

        if not child.leaf:
            new_child.children = child.children[t:]
            child.children = child.children[:t]

    def insert(self, key, value):
        root = self.root
        if root.is_full():
            new_root = BTreeNode(self.t, leaf=False)
            new_root.children.append(root)
            self.split_child(new_root, 0, root)
            self.root = new_root
            self._insert_non_full(new_root, key, value)
        else:
            self._insert_non_full(root, key, value)

    def _insert_non_full(self, node, key, value):
        i = len(node.keys) - 1

        if node.leaf:
            node.keys.append(None)
            node.values.append(None)

            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1

            node.keys[i + 1] = key
            node.values[i + 1] = value

        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1

            i += 1
            if node.children[i].is_full():
                self.split_child(node, i, node.children[i])
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key, value)

    def remove(self, key):
        # lista tudo em ordem
        data = self.inorder()

        # filtra removendo a key
        new_data = [(k, v) for (k, v) in data if k != key]

        # depois reconstrói a árvore
        self.root = BTreeNode(self.t, leaf=True)
        for k, v in new_data:
            self.insert(k, v)

    def update_password(self, key, new_password):
        result = self.search(self.root, key)
        if result:
            node, idx = result
            node.values[idx] = new_password
            return True
        return False

    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        for i in range(len(node.keys)):
            if not node.leaf:
                self._inorder(node.children[i], result)
            result.append((node.keys[i], node.values[i]))
        if not node.leaf:
            self._inorder(node.children[-1], result)
