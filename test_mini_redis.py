
"""Mini Redis 필수 미션 검증용 자동 테스트.

실행: python3 -m unittest -v test_mini_redis
외부 패키지 설치 불필요(Python 표준 라이브러리만 사용).
"""

import unittest
from unittest.mock import patch

from doubly_linked import DoublyLinkedList
from hash_map import HashMap
from min_heap import MinHeap
from mini_redis import MiniRedis
from main import execute_command


class TestDoublyLinkedList(unittest.TestCase):
    def test_insert_move_remove(self):
        linked = DoublyLinkedList()
        a = linked.insert_back("A")
        b = linked.insert_back("B")
        c = linked.insert_front("C")
        self.assertEqual((linked.head.data, linked.tail.data, linked.length), ("C", "B", 3))
        linked.move_to_front(b)
        self.assertEqual((linked.head.data, linked.tail.data, linked.length), ("B", "A", 3))
        linked.remove_node(a)
        self.assertEqual(linked.length, 2)
        self.assertEqual(linked.remove_front().data, "B")
        self.assertEqual(linked.remove_back().data, "C")
        self.assertEqual(linked.length, 0)
        self.assertIsNone(linked.head)
        self.assertIsNone(linked.tail)


class TestHashMap(unittest.TestCase):
    def test_collision_and_individual_deletion(self):
        h = HashMap()
        self.assertEqual(h._hash("AB"), h._hash("AJ"))
        h.put("AB", "Alice")
        h.put("AJ", "John")
        self.assertEqual(h.get("AB"), "Alice")
        self.assertEqual(h.get("AJ"), "John")
        self.assertEqual(h.size(), 2)
        self.assertTrue(h.remove("AB"))
        self.assertIsNone(h.get("AB"))
        self.assertEqual(h.get("AJ"), "John")
        self.assertEqual(h.size(), 1)

    def test_resize_rehash_and_overwrite(self):
        h = HashMap()
        for i in range(7):
            h.put("user:" + str(i), "value:" + str(i))
        self.assertEqual(h.capacity, 16)
        self.assertEqual(h.size(), 7)
        for i in range(7):
            self.assertEqual(h.get("user:" + str(i)), "value:" + str(i))
        h.put("user:3", "updated")
        self.assertEqual(h.get("user:3"), "updated")
        self.assertEqual(h.size(), 7)
        self.assertTrue(h.contains("user:3"))
        self.assertFalse(h.contains("missing"))


class TestMinHeap(unittest.TestCase):
    def test_minimum_first_and_capacity_growth(self):
        h = MinHeap()
        for n in [30, 10, 20, 40, 5]:
            h.push((n, "key" + str(n)))
        self.assertEqual(h.capacity, 8)
        self.assertEqual(h.peek()[0], 5)
        self.assertEqual([h.pop()[0] for _ in range(5)], [5, 10, 20, 30, 40])
        self.assertIsNone(h.pop())
        self.assertIsNone(h.peek())


class TestMiniRedis(unittest.TestCase):
    def setUp(self):
        self.r = MiniRedis()

    def test_basic_set_get_del_exists(self):
        self.assertEqual(self.r.set("name", "Alice"), "OK")
        self.assertEqual(self.r.get("name"), '"Alice"')
        self.assertEqual(self.r.exists("name"), "(integer) 1")
        self.assertEqual(self.r.delete("name"), "(integer) 1")
        self.assertEqual(self.r.get("name"), "(nil)")
        self.assertEqual(self.r.exists("name"), "(integer) 0")
        self.assertEqual(self.r.delete("name"), "(integer) 0")

    def test_dbsize_and_keys(self):
        self.assertEqual(self.r.dbsize(), "(integer) 0")
        self.assertEqual(self.r.keys(), "(empty array)")
        self.r.set("A", "1")
        self.r.set("B", "2")
        self.assertEqual(self.r.dbsize(), "(integer) 2")
        result = self.r.keys()
        self.assertIn('"A"', result)
        self.assertIn('"B"', result)

    def test_utf8_memory_accounting_and_overwrite(self):
        self.r.set("한", "글")
        self.assertEqual(self.r.used_memory, 6)
        self.r.set("한", "A")
        self.assertEqual(self.r.used_memory, 4)
        self.assertEqual(self.r.dbsize(), "(integer) 1")

    def test_lru_eviction_order(self):
        self.assertEqual(self.r.config_set_maxmemory(20), "OK")
        for key in ("A", "B", "C"):
            self.assertEqual(self.r.set(key, "12345"), "OK")
        self.assertEqual(self.r.get("A"), '"12345"')
        self.assertEqual(self.r.set("D", "123645"), "OK")
        self.assertEqual(self.r.get("B"), "(nil)")
        self.assertEqual(self.r.used_memory, 19)
        self.assertEqual(self.r.evicted_keys, 1)
        self.assertEqual(self.r.dbsize(), "(integer) 3")

    def test_oom_does_not_modify_existing_keys(self):
        self.r.config_set_maxmemory(20)
        self.r.set("A", "12345")
        self.r.set("B", "12345")
        result = self.r.set("BUG", "12345678901234567890")
        self.assertIn("OOM", result)
        self.assertEqual(self.r.get("BUG"), "(nil)")
        self.assertEqual(self.r.used_memory, 12)
        self.assertEqual(self.r.evicted_keys, 0)
        self.assertEqual(self.r.dbsize(), "(integer) 2")

    def test_config_zero_unlimited_and_invalid(self):
        self.assertEqual(self.r.config_set_maxmemory(0), "OK")
        self.assertIn("maxmemory:0", self.r.info_memory())
        self.assertIn("(error)", self.r.config_set_maxmemory(-1))

    def test_ttl_no_expiry_and_missing(self):
        self.assertEqual(self.r.ttl("missing"), "(integer) -2")
        self.r.set("A", "1")
        self.assertEqual(self.r.ttl("A"), "(integer) -1")
        self.assertEqual(self.r.expire("missing", 10), "(integer) 0")

    def test_ttl_expiration_removes_key_and_memory(self):
        with patch("mini_redis.time.time", return_value=1000.0):
            self.r.set("A", "12345")
            self.assertEqual(self.r.expire("A", 5), "(integer) 1")
        with patch("mini_redis.time.time", return_value=1006.0):
            self.assertEqual(self.r.get("A"), "(nil)")
            self.assertEqual(self.r.ttl("A"), "(integer) -2")
            self.assertEqual(self.r.used_memory, 0)
            self.assertEqual(self.r.dbsize(), "(integer) 0")

    def test_expire_zero_deletes_immediately(self):
        self.r.set("A", "1")
        self.assertEqual(self.r.expire("A", 0), "(integer) 1")
        self.assertEqual(self.r.get("A"), "(nil)")

    def test_set_overwrite_clears_ttl(self):
        with patch("mini_redis.time.time", return_value=1000.0):
            self.r.set("A", "before")
            self.r.expire("A", 2)
            self.r.set("A", "after")
        with patch("mini_redis.time.time", return_value=1010.0):
            self.assertEqual(self.r.get("A"), '"after"')
            self.assertEqual(self.r.ttl("A"), "(integer) -1")

    def test_repeated_expire_ignores_stale_heap_entry(self):
        with patch("mini_redis.time.time", return_value=1000.0):
            self.r.set("A", "Hello")
            self.r.expire("A", 2)
            self.r.expire("A", 120)
        with patch("mini_redis.time.time", return_value=1003.0):
            self.assertEqual(self.r.dbsize(), "(integer) 1")
            self.assertEqual(self.r.get("A"), '"Hello"')
            self.assertEqual(self.r.ttl("A"), "(integer) 117")

    def test_delete_cleans_expiry_and_lru(self):
        self.r.set("A", "x")
        self.r.expire("A", 60)
        self.assertEqual(self.r.delete("A"), "(integer) 1")
        self.assertFalse(self.r.lru_nodes.contains("A"))
        self.assertFalse(self.r.expires.contains("A"))
        self.assertEqual(self.r.lru.length, 0)
        self.assertEqual(self.r.used_memory, 0)

    def test_info_memory_fields(self):
        info = self.r.info_memory()
        self.assertIn("used_memory:", info)
        self.assertIn("maxmemory:", info)
        self.assertIn("evicted_keys:", info)


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.r = MiniRedis()

    def test_quotes_and_command_parsing(self):
        self.assertEqual(execute_command(self.r, 'SET greeting "Hello World"'), "OK")
        self.assertEqual(execute_command(self.r, "GET greeting"), '"Hello World"')
        self.assertEqual(execute_command(self.r, "DBSIZE"), "(integer) 1")

    def test_invalid_commands_and_arguments(self):
        self.assertIn("unknown command", execute_command(self.r, "HELLO"))
        self.assertIn("wrong number of arguments", execute_command(self.r, "GET"))
        self.assertIn("not an integer", execute_command(self.r, "EXPIRE A abc"))
        self.assertIn("not an integer", execute_command(self.r, "CONFIG SET maxmemory abc"))
        self.assertIn("invalid quotes", execute_command(self.r, 'SET A "oops'))


if __name__ == "__main__":
    unittest.main(verbosity=2)
