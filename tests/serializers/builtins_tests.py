from pytrace.serializers import builtins, ObjectSerializer
from pytrace.conf import settings

from . import SerializerTestCase


class PremitiveTypeSerializerTests(SerializerTestCase):

    serializer_class = builtins.PremitiveTypeSerializer

    def assertPremitiveSerialization(self, value):
        encoded_value = self.serialize(value)
        self.assertEqual(encoded_value, repr(value))

    def test_serialization(self):
        for type_ in settings.PRIMITIVE_TYPES:
            if isinstance(None, type_):
                continue  # NoneType can't be initialized
            self.assertPremitiveSerialization(type_())

    def test_none_serialization(self):
        self.assertPremitiveSerialization(None)


class TypeSerializerTests(SerializerTestCase):

    serializer_class = builtins.TypeSerializer

    def test_serialization(self):
        encoded_value = self.serializer.serialize(int)
        self.assertEncodedType(encoded_value, int)


def _test_function(arg1, arg2, *args, **extras):
    "Test Function"
    pass


class FunctionSerializerTests(SerializerTestCase):

    serializer_class = builtins.FunctionSerializer

    def assertFunctionSerialization(self, encoded_value, function):
        self.assertContains(encoded_value, 'arguments',
                            'isLambda', 'lineno', 'parent', 'help')
        self.assertEqual(encoded_value['help'], function.__doc__)

        arguments = encoded_value['arguments']
        self.assertContains(arguments, 'args', 'varargs', 'keywords')

    def test_function_serialization(self):
        encoded_value = self.serialize(_test_function)
        self.assertFunctionSerialization(encoded_value, _test_function)
        self.assertEqual(encoded_value['isLambda'], False)

    def test_lambda_serialization(self):
        lambda_func = lambda x: x ** x  # NOQA
        encoded_value = self.serialize(lambda_func)
        self.assertFunctionSerialization(encoded_value, lambda_func)
        self.assertEqual(encoded_value['isLambda'], True)


class MethodSerializerTests(SerializerTestCase):

    serializer_class = builtins.MethodSerializer

    def test_serialization(self):
        encoded_value = self.serialize(self.test_serialization)
        self.assertIn('class', encoded_value)

        owner_class_id = encoded_value['class']
        owner_class = ObjectSerializer().get_object_by_id(owner_class_id)
        self.assertContains(owner_class, 'name', 'module')
        self.assertEqual(owner_class['name'], type(self).__name__)
        self.assertEqual(owner_class['module'], type(self).__module__)


class ModuleSerializerTests(SerializerTestCase):

    serializer_class = builtins.ModuleSerializer

    def test_serialization(self):
        import math
        encoded_value = self.serialize(math)
        self.assertContains(encoded_value, 'version', 'package', 'attributes')


class ClassSerializerTests(SerializerTestCase):

    serializer_class = builtins.ClassSerializer

    def test_serialization(self):
        encoded_value = self.serialize(type(self))
        self.assertContains(encoded_value, 'super', 'attributes')
        self.assertEquals(len(encoded_value['super']), 1)
