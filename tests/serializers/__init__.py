import unittest2
from pytrace.serializers import ObjectSerializer


class SerializerTestCase(unittest2.TestCase):

    serializer_class = None

    def setUp(self):
        self.serializer = self.serializer_class()
        self.parent_serializer = ObjectSerializer()
        self.serializer.parent = self.parent_serializer

    def assertContains(self, container, *items):
        for item in items:
            self.assertIn(item, container)

    def assertEncodedType(self, encoded_value, type_):
        self.assertContains(encoded_value, 'name', 'module')
        self.assertEqual(encoded_value['name'], type_.__name__)
        self.assertEqual(encoded_value['module'], type_.__module__)

    def serialize(self, value):
        response = self.serializer.serialize(value)
        self.assertContains(response, 'type', 'value', 'name')
        self.assertEncodedType(response['type'], type(value))
        return response['value']
