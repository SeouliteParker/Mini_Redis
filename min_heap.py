


class MinHeap:
    """TTL 만료 시간을 관리하는 최소 힙"""

    def __init__(self):
        """초기 용량 4칸의 힙을 생성한다."""
        self.capacity = 4
        self.count = 0
        self.heap = [None] * self.capacity

    def size(self):
        """실제로 저장된 데이터 개수를 반환한다."""
        return self.count

    def _resize(self):
        """저장 공간이 부족하면 배열을 2배 확장한다."""
        new_capacity = self.capacity * 2
        new_heap = [None] * new_capacity

        for i in range(self.count):
            new_heap[i] = self.heap[i]

        self.heap = new_heap
        self.capacity = new_capacity

    def push(self, item):
        """데이터를 추가하고 최소 힙 구조를 유지한다."""

        if self.count == self.capacity:
            self._resize()

        self.heap[self.count] = item
        self.count += 1

        self._heapify_up(self.count - 1)

    def _heapify_up(self, index):
        """새 노드를 부모와 비교하며 위로 이동한다."""

        while index > 0:
            parent = (index - 1) // 2

            if self.heap[parent][0] <= self.heap[index][0]:
                break

            self.heap[parent], self.heap[index] = (
                self.heap[index], self.heap[parent]
            )

            index = parent

    
    def peek(self):
        """가장 작은 값을 삭제하지 않고 반환한다."""

        if self.size() == 0:
            return None

        return self.heap[0]


    def pop(self):
        """가장 작은 데이터를 제거하고 반환한다."""

        if self.count == 0:
            return None

        min_item = self.heap[0]

        self.count -= 1

        if self.count == 0:
            self.heap[0] = None
            return min_item

        self.heap[0] = self.heap[self.count]
        self.heap[self.count] = None

        self._heapify_down(0)

        return min_item

    def _heapify_down(self, index):
        """부모를 자식과 비교하면서 아래로 이동한다."""

        size = self.size()

        while True:
            left = 2 * index + 1
            right = 2 * index + 2
            smallest = index

            if (left < size and
                    self.heap[left][0] < self.heap[smallest][0]):
                smallest = left

            if (right < size and
                    self.heap[right][0] < self.heap[smallest][0]):
                smallest = right

            if smallest == index:
                break

            self.heap[index], self.heap[smallest] = (
                self.heap[smallest], self.heap[index]
            )

            index = smallest

if __name__ == "__main__":
    my_heap = MinHeap()

    my_heap.push((30, "user:1"))
    my_heap.push((10, "user:2"))
    my_heap.push((20, "user:3"))
    my_heap.push((40, "user:4"))
    my_heap.push((5, "user:5"))

    print("배열 용량:", my_heap.capacity)
    print("데이터 개수:", my_heap.size())
    print("가장 작은 값:", my_heap.peek())

    while my_heap.size() > 0:
        print("삭제:", my_heap.pop())

