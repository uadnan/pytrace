import sys
from abc import abstractmethod
import six

from pytrace.core.exceptions import NoSerializerFoundError, SerializationError
from pytrace.core.heap import Heap

from pytrace.utils.functional import Singleton

from .registry import default as serializers_registry


class AbstractSerializer(object):
    """
    Base class for all serializers
    """

    def get_object_name(self, obj):
        """ Get friendly name of object """
        if hasattr(obj, '__name__'):
            return obj.__name__

        return self.get_object_name(type(obj))

    def encode_type(self, type_):
        return {
            'name': type_.__name__,
            'module': type_.__module__
        }

    def serialize(self, obj):
        return {
            'name': self.get_object_name(obj),
            'type': self.encode_type(type(obj)),
            'value': self.encode(obj)
        }

    def serialize_inner(self, value):
        return ObjectSerializer().encode(value)

    @abstractmethod
    def encode(self, obj):
        pass


@six.add_metaclass(Singleton)
class ObjectSerializer(object):

    def __init__(self):
        self.heap = Heap()
        self.reset()

    def reset(self):
        self._buffer = {}
        self.heap.reset()

    def get_object_by_id(self, id_):
        return self.heap[id_]

    def _cache(self, original, encoded):
        self._buffer[id(original)] = encoded

    def _cached_encoded_value(self, original):
        return self._buffer.get(id(original), None)

    def encode_using(self, value, serializer):
        try:
            encoded_value = serializer.serialize(value)
            self._cache(value, encoded_value)
            return encoded_value
        except NoSerializerFoundError:
            raise
        except Exception as ex:
            _, _, tb = sys.exc_info()
            six.reraise(SerializationError, (serializer, value, ex), tb)

    def encode(self, value):
        value_type = type(value)
        encoded_value = self._cached_encoded_value(value)
        if not encoded_value:  # If in cache, don't serialize again
            serializer = serializers_registry.get(value_type)
            if serializer is None:
                raise NoSerializerFoundError(value_type)

            encoded_value = self.encode_using(value, serializer)

        return self.heap.store(encoded_value, actual_value=value)
