from pytrace.serializers import fallback
from pytrace.core.builtins import InputFunction, ImportStatement
from six import PY2

from . import SerializerTestCase


class FallbackSerializerTests(SerializerTestCase):

    serializer_class = fallback.FallbackSerializer

    def test_exception_serialization(self):
        encoded_value = self.serialize(ValueError("O Really?"))
        self.assertContains(encoded_value, "message", "type")
        self.assertEqual(encoded_value["type"], "ValueError")

    def test_old_class_instance(self):

        class OldStyleClass:
            def __init__(self):
                pass

        encoded_value = self.serialize(OldStyleClass())
        self.assertContains(encoded_value, "attributes", "class")

    def test_mocked_import(self):
        statement = ImportStatement()
        results = self.serializer.serialize(statement)
        self.assertEncodedType(results["type"], type(__import__))
        self.assertEqual(results["name"], "__import__")

        encoded_value = results["value"]
        self.assertContains(encoded_value, "help")
        self.assertEqual(encoded_value["help"], statement.__doc__)

    def test_mocked_input(self):
        function = InputFunction()
        results = self.serializer.serialize(function)
        input_func = __builtins__['raw_input' if PY2 else 'input']
        self.assertEncodedType(results["type"], type(input_func))
        self.assertEqual(results["name"], input_func.__name__)

        encoded_value = results["value"]
        self.assertContains(encoded_value, "help")
        self.assertEqual(encoded_value["help"], function.__doc__)
