class Node:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def insert_front(self, data):
        new_node = Node(data)

        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node

        self.length += 1
        return new_node


    def insert_back(self, data):
        """리스트 맨 뒤에 새로운 노드를 추가한다."""
        new_node = Node(data)

        if self.tail is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node

        self.length += 1
        return new_node

    
    def remove_front(self):
        """맨 앞 노드를 제거하고 반환한다."""

        if self.head is None:
            return None

        removed_node = self.head
        self.head = self.head.next

        if self.head is None:
            self.tail = None
        else:
            self.head.prev = None

        removed_node.prev = None
        removed_node.next = None

        self.length -= 1
        return removed_node

    def remove_back(self):
        """맨 뒤 노드를 제거하고 반환한다."""

        if self.tail is None:
            return None

        removed_node = self.tail
        self.tail = self.tail.prev

        if self.tail is None:
            self.head = None
        else:
            self.tail.next = None

        removed_node.prev = None
        removed_node.next = None

        self.length -= 1
        return removed_node

    
    def remove_node(self, node):
        """지정한 노드를 리스트에서 제거한다."""

        if node is None:
            return None

        if node is self.head:
            return self.remove_front()

        if node is self.tail:
            return self.remove_back()

        node.prev.next = node.next
        node.next.prev = node.prev

        node.prev = None
        node.next = None

        self.length -= 1
        return node

    
    def move_to_front(self, node):
        """기존 노드를 리스트 맨 앞으로 이동한다."""

        if node is None or node is self.head:
            return

        # 기존 위치에서 노드 분리
        if node is self.tail:
            self.tail = node.prev
            self.tail.next = None
        else:
            node.prev.next = node.next
            node.next.prev = node.prev

        # 맨 앞에 다시 연결
        node.prev = None
        node.next = self.head
        self.head.prev = node
        self.head = node

if __name__ == "__main__":
    my_list = DoublyLinkedList()

    alice = my_list.insert_back("Alice")
    bob = my_list.insert_back("Bob")
    charlie = my_list.insert_back("Charlie")

    my_list.move_to_front(charlie)

    print(my_list.head.data)
    print(my_list.tail.data)
    print(my_list.length)

