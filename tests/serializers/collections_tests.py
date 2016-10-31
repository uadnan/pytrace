from pytrace.serializers import collections

from . import SerializerTestCase


class CollectionSerializerTests(SerializerTestCase):

    serializer_class = collections.CollectionSerializer

    def test_list_serialization(self):
        encoded_value = self.serialize([1, 2, 3])
        self.assertEqual(len(encoded_value), 3)

    def test_tuple_serialization(self):
        encoded_value = self.serialize((1, 2, 3))
        self.assertEqual(len(encoded_value), 3)

    def test_set_serialization(self):
        encoded_value = self.serialize(set([1, 2, 3]))
        self.assertEqual(len(encoded_value), 3)

    def test_circular_list1(self):
        lst = [1]
        lst.append(lst)
        encoded_value = self.serialize(lst)
        self.assertEqual(encoded_value[1], "[...]")

    def test_circular_list2(self):
        lst = [1]
        lst.append(lst)

        encoded_value = self.serialize([lst])
        inner_list = self.parent_serializer.get_object_by_id(encoded_value[0])
        self.assertEqual(inner_list['value'][1], "[...]")


class DictionarySerializerTests(SerializerTestCase):

    serializer_class = collections.DictionarySerializer

    def test_serialization(self):
        encoded_value = self.serialize({1: 2, 3: 4})
        self.assertEqual(len(encoded_value), 2)

    def test_circular_dict1(self):
        dct = {1: 2}
        dct[2] = dct
        encoded_value = self.serialize(dct)
        e2 = list(encoded_value.keys())[1]
        self.assertEqual(encoded_value[e2], "{...}")
