import unittest2

from pytrace.core.heap import Heap


class HeapTests(unittest2.TestCase):

    def test_store(self):
        store = Heap()
        store.store([1, 2, 3])
        self.assertEqual(len(store), 1)

    def test_generated_uid(self):
        store = Heap()
        uid = store.store([1, 2, 3])
        self.assertIsInstance(uid, str)
        self.assertEqual(uid, "0x1")

    def test_duplicate_item(self):
        store = Heap()
        item = [1, 2, 3]
        uid1 = store.store(item)
        uid2 = store.store(item)
        self.assertEqual(uid1, uid2)
        self.assertEqual(len(store), 1)

    def test_reset(self):
        store = Heap()
        store.store(1)
        store.store([1, 3, 4])
        store.store([4, 5, 6])

        store.reset()
        self.assertEqual(len(store), 1)  # Const must be there
