

from hash_map import HashMap
from doubly_linked import DoublyLinkedList
from min_heap import MinHeap
import time


class MiniRedis:
    """Mini Redis의 데이터 저장 및 관리 엔진"""

    def __init__(self):
        self.data = HashMap()
        self.lru = DoublyLinkedList()
        self.lru_nodes = HashMap()
        self.ttl_heap = MinHeap()
        self.expires = HashMap()

        self.maxmemory = 0
        self.used_memory = 0
        self.evicted_keys = 0

    def _entry_size(self, key, value):
        """키와 값의 UTF-8 바이트 크기를 계산한다."""

        key_size = len(key.encode("utf-8"))
        value_size = len(value.encode("utf-8"))

        return key_size + value_size

    def _touch(self, key):
        """사용한 키를 LRU 리스트 맨 앞으로 이동한다."""

        node = self.lru_nodes.get(key)

        if node is not None:
            self.lru.move_to_front(node)
        else:
            new_node = self.lru.insert_front(key)
            self.lru_nodes.put(key, new_node)

    def set(self, key, value):
        """데이터 저장, 메모리 계산, LRU 자동 제거"""

        self._check_expired(key)
        new_size = self._entry_size(key, value)

        # 단일 데이터가 최대 메모리보다 크면 저장 거부
        if self.maxmemory > 0 and new_size > self.maxmemory:
            return "(error) OOM command not allowed when used_memory > 'maxmemory'"

        old_value = self.data.get(key)

        if old_value is not None:
            self.used_memory -= self._entry_size(key, old_value)

        self.data.put(key, value)
        self.expires.remove(key)
        self.used_memory += new_size

        self._touch(key)
        self._evict_lru()

        return "OK"

    def get(self, key):
        """키의 값을 조회하고 LRU를 갱신한다."""
        self._check_expired(key)
        value = self.data.get(key)

        if value is None:
            return "(nil)"

        self._touch(key)
        return '"' + value + '"'

    def config_set_maxmemory(self, bytes_limit):
        """최대 메모리 사용량을 설정한다."""

        if type(bytes_limit) is not int or bytes_limit < 0:
            return "(error) ERR value is not an integer or out of range"

        self.maxmemory = bytes_limit
        self._evict_lru()

        return "OK"

    def info_memory(self):
        """메모리 사용 정보를 반환한다."""
        self._purge_expired()
        return (
            f"used_memory:{self.used_memory}\n"
            f"maxmemory:{self.maxmemory}\n"
            f"evicted_keys:{self.evicted_keys}"
        )


    def _delete_key(self, key):
        """데이터와 LRU 정보를 함께 삭제한다."""

        value = self.data.get(key)

        if value is None:
            return False

        self.used_memory -= self._entry_size(key, value)

        node = self.lru_nodes.get(key)

        if node is not None:
            self.lru.remove_node(node)
            self.lru_nodes.remove(key)

        self.data.remove(key)
        self.expires.remove(key)

        return True

    def _evict_lru(self):
        """만료 데이터를 정리하고 필요하면 LRU 키를 제거한다."""

        # 1. 만료된 데이터를 먼저 삭제
        self._purge_expired()

        # 2. 메모리 제한 초과 여부 확인
        while self.maxmemory > 0 and self.used_memory > self.maxmemory:

            if self.lru.tail is None:
                break

            # 3. 가장 오래 사용하지 않은 키 선택
            oldest_key = self.lru.tail.data

            # 4. 데이터 삭제 및 제거 횟수 기록
            if self._delete_key(oldest_key):
                self.evicted_keys += 1
            else:
                break

    def delete(self, key):
        """키를 삭제한다."""
        self._check_expired(key)

        if self._delete_key(key):
            return "(integer) 1"

        return "(integer) 0"

    def exists(self, key):
        """키 존재 여부를 확인한다."""
        self._purge_expired()

        if self.data.contains(key):
            return "(integer) 1"

        return "(integer) 0"

    def dbsize(self):
        """만료되지 않은 전체 키 개수를 반환한다."""
        self._purge_expired()

        return f"(integer) {self.data.size()}"

    def keys(self):
        """만료되지 않은 전체 키 목록을 반환한다."""
        self._purge_expired()

        all_keys = self.data.keys()

        if len(all_keys) == 0:
            return "(empty array)"

        result = ""

        for i in range(len(all_keys)):
            result += f'{i + 1}. "{all_keys[i]}"\n'

        return result.rstrip()

    def expire(self, key, seconds):
        """키의 만료 시간을 설정한다."""

        self._check_expired(key)

        if not self.data.contains(key):
            return "(integer) 0"

        if seconds <= 0:
            self._delete_key(key)
            return "(integer) 1"

        expire_at = time.time() + seconds

        self.expires.put(key, expire_at)
        self.ttl_heap.push((expire_at, key))

        return "(integer) 1"


    def _check_expired(self, key):
        """키가 만료되었으면 삭제한다."""

        expire_at = self.expires.get(key)

        if expire_at is None:
            return

        if time.time() >= expire_at:
            self._delete_key(key)


    def _purge_expired(self):
        """최소 힙을 이용해 만료된 키들을 정리한다."""

        now = time.time()

        while self.ttl_heap.size() > 0:
            item = self.ttl_heap.peek()

            expire_at, key = item

            if expire_at > now:
                break

            self.ttl_heap.pop()

            current_expire = self.expires.get(key)

            if current_expire == expire_at:
                self._delete_key(key)

    def ttl(self, key):
        """키의 남은 만료 시간을 초 단위로 반환한다."""

        self._check_expired(key)

        if not self.data.contains(key):
            return "(integer) -2"

        expire_at = self.expires.get(key)

        if expire_at is None:
            return "(integer) -1"

        remaining = max(0, int(expire_at - time.time()))

        return f"(integer) {remaining}"


if __name__ == "__main__":
    redis = MiniRedis()

    redis.set("user:1", "Alice")
    redis.set("user:2", "Bob")

    # user:1은 1초 후 만료
    redis.expire("user:1", 1)

    time.sleep(2)

    # 새로운 데이터 저장
    redis.set("user:3", "Charlie")

    # 메모리 제한 적용
    print(redis.config_set_maxmemory(30))

    print("user:1:", redis.get("user:1"))
    print("user:2:", redis.get("user:2"))
    print("user:3:", redis.get("user:3"))

    print(redis.info_memory())
