
from doubly_linked import DoublyLinkedList


class Entry:
    """해시맵에 저장할 키와 값"""

    def __init__(self, key, value):
        self.key = key
        self.value = value


class HashMap:
    """체이닝 방식의 해시맵"""

    def __init__(self):
        self.capacity = 8
        self.count = 0
        self.buckets = [None] * self.capacity

    def _hash(self, key):
        """문자열 키를 버킷 인덱스로 변환한다."""

        hash_value = 0

        for char in key:
            hash_value = hash_value * 31 + ord(char)

        return hash_value % self.capacity

    
    def put(self, key, value):
        """키와 값을 해시맵에 저장한다."""

        index = self._hash(key)

        if self.buckets[index] is None:
            self.buckets[index] = DoublyLinkedList()

        bucket = self.buckets[index]

        current = bucket.head

        while current is not None:
            if current.data.key == key:
                current.data.value = value
                return

            current = current.next

        bucket.insert_back(Entry(key, value))
        self.count += 1

        if self.count / self.capacity > 0.75:
            self._resize()

    def get(self, key):
        """키에 해당하는 값을 찾아 반환한다."""

        index = self._hash(key)
        bucket = self.buckets[index]

        if bucket is None:
            return None

        current = bucket.head

        while current is not None:
            if current.data.key == key:
                return current.data.value

            current = current.next

        return None

    
    def remove(self, key):
        """키에 해당하는 항목을 삭제한다."""

        index = self._hash(key)
        bucket = self.buckets[index]

        if bucket is None:
            return False

        current = bucket.head

        while current is not None:
            if current.data.key == key:
                bucket.remove_node(current)
                self.count -= 1

                if bucket.length == 0:
                    self.buckets[index] = None

                return True

            current = current.next

        return False

    
    def contains(self, key):
        """키가 존재하면 True, 없으면 False를 반환한다."""

        index = self._hash(key)
        bucket = self.buckets[index]

        if bucket is None:
            return False

        current = bucket.head

        while current is not None:
            if current.data.key == key:
                return True

            current = current.next

        return False


    def keys(self):
        """해시맵의 모든 키를 반환한다."""

        result = []

        for bucket in self.buckets:
            if bucket is None:
                continue

            current = bucket.head

            while current is not None:
                result.append(current.data.key)
                current = current.next

        return result

    def size(self):
        """현재 저장된 키의 개수를 반환한다."""
        return self.count

    
    def _resize(self):
        """버킷 수를 2배로 늘리고 데이터를 재배치한다."""

        old_buckets = self.buckets

        self.capacity *= 2
        self.buckets = [None] * self.capacity

        for bucket in old_buckets:
            if bucket is None:
                continue

            current = bucket.head

            while current is not None:
                entry = current.data
                index = self._hash(entry.key)

                if self.buckets[index] is None:
                    self.buckets[index] = DoublyLinkedList()

                self.buckets[index].insert_back(entry)

                current = current.next

if __name__ == "__main__":
    my_map = HashMap()

    print("초기 버킷:", my_map.capacity)

    for i in range(1, 8):
        key = "user:" + str(i)
        value = "User" + str(i)

        my_map.put(key, value)

        print(
            "데이터:", my_map.size(),
            "버킷:", my_map.capacity
        )

    print("user:1 조회:", my_map.get("user:1"))
    print("user:7 조회:", my_map.get("user:7"))
