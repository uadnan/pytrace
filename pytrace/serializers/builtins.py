import inspect
import types
from abc import abstractmethod
import six

from pytrace.conf import settings
from pytrace import compat

from .registry import default as registry
from .base import AbstractSerializer


@registry.register_class(*settings.PRIMITIVE_TYPES)
class PremitiveTypeSerializer(AbstractSerializer):
    """
    Serializer for type interpreted as primitive
    This will simply invokes object.__repr__
    """

    def encode(self, value):
        return repr(value)


@registry.register_class(compat.TypeType)
class TypeSerializer(AbstractSerializer):
    """
    Serializer for type`
    """

    def encode(self, value):
        return {
            'name': value.__name__,
            'module': value.__module__
        }

    serialize = encode 


@registry.register_class(types.FunctionType)
class FunctionSerializer(AbstractSerializer):

    def get_arguments(self, obj):
        argspec = inspect.getargspec(obj)

        return {
            'args': list(argspec.args),
            'varargs': argspec.varargs,
            'keywords': argspec.keywords
        }

    def get_parent(self, func):
        if hasattr(func, '__parent__') and func.__parent__ is not None:
            return self.serialize_inner(func.__parent__)

    def encode(self, value):
        is_lambda = compat.is_lambda(value)
        func_code = compat.get_func_code(value)

        return {
            'arguments': self.get_arguments(value),
            'isLambda': is_lambda,
            'lineno': func_code.co_firstlineno,
            'parent': self.get_parent(value),
            'help': value.__doc__ if hasattr(value, '__doc__') else None
        }


@registry.register_class(types.MethodType)
class MethodSerializer(FunctionSerializer):
    """
    Serializer for method or class bound functions
    """

    def encode(self, value):
        encoded_value = super(MethodSerializer, self).encode(value)
        owner_class = compat.get_im_class(value)
        encoded_value['class'] = self.serialize_inner(owner_class)
        return encoded_value


@registry.register_class(types.BuiltinFunctionType, types.BuiltinMethodType)
class BuiltinFunctionSerializer(AbstractSerializer):
    """
    Serializer for builtin function and builtin bounded functions or methods
    """

    def encode(self, value):
        return {
            'help': value.__doc__ if hasattr(value, '__doc__') else None
        }


class AttributeSerializer(AbstractSerializer):

    @abstractmethod
    def encode(self, value):
        pass

    def filter_attributes(self, dctx):
        return sorted([
            e for e in dctx
            if not e.startswith('__')
        ])

    def encode_attributes(self, value):
        attrs = {}

        if hasattr(value, '__dict__'):
            for atr in self.filter_attributes(value.__dict__):
                attrValue = getattr(value, atr)
                attrs[atr] = self.serialize_inner(attrValue)

        return attrs


@registry.register_class(types.ModuleType)
class ModuleSerializer(AttributeSerializer):

    def encode(self, value):
        return {
            'version': str(getattr(value, '__version__', None) or ''),
            'package': str(getattr(value, '__package__', None) or ''),
            'attributes': self.encode_attributes(value)
        }


class ClassSerializer(AttributeSerializer):

    def encode(self, value):
        return {
            'super': [
                self.serialize_inner(e)
                for e in value.__bases__
                if e is not object
            ],
            'attributes': self.encode_attributes(value)
        }


class InstanceSerializer(AttributeSerializer):

    def encode(self, value):
        klass = value.__class__ if hasattr(value, '__class__') else type(value)
        return {
            'class': self.serialize_inner(klass),
            'attributes': self.encode_attributes(value)
        }

if six.PY2:
    registry.register_class(types.ClassType)(ClassSerializer)
    registry.register_class(types.InstanceType)(InstanceSerializer)
