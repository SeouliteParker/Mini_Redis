class Node:

    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None

node1 = Node("Alice")

print(node1.data)
print(node1.prev)
print(node1.next)            