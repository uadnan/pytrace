import types

from pytrace.core.builtins import BuiltinBase
from pytrace.compat import is_class_instance

from .registry import default as registry
from .builtins import (
    InstanceSerializer, BuiltinFunctionSerializer, ClassSerializer
)
from .base import AbstractSerializer


@registry.default
class FallbackSerializer(AbstractSerializer):

    def encode_type(self, type_):
        if BuiltinBase in type.mro(type_):
            type_ = types.BuiltinFunctionType

        return super(FallbackSerializer, self).encode_type(type_)

    def encode_exception(self, value):
        return {
            'type': type(value).__name__,
            'message': str(value)
        }

    def encode(self, value):
        mro = type.mro(type(value))
        if BaseException in mro:
            return self.encode_exception(value)

        if BuiltinBase in mro:
            return BuiltinFunctionSerializer().encode(value)

        if isinstance(value, type):
            return ClassSerializer().encode(value)

        if is_class_instance(value):
            return InstanceSerializer().encode(value)

        return repr(value)
