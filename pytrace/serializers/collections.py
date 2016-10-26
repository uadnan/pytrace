from abc import abstractmethod

from .registry import default as registry
from .base import AbstractSerializer


class AbstractCollectionSerializer(AbstractSerializer):

    def __init__(self, *args, **kwargs):
        super(AbstractCollectionSerializer, self).__init__(*args, **kwargs)
        self.reset_parent_footprint()

    def get_parent(self, item):
        return self._parent_footprint.get(id(item), None)

    def set_parent(self, item, parent):
        self._parent_footprint[id(item)] = parent

    def reset_parent_footprint(self):
        self._parent_footprint = {}

    def is_self(self, collection, item):
        while item is not None:
            if collection == item:
                return True

            item = self.get_parent(item)

        return False

    def encode(self, value):
        encoded_value = self.encode_collection(value)
        self.reset_parent_footprint()
        return encoded_value

    @abstractmethod
    def encode_collection(self, collection):
        pass


@registry.register_class(list, tuple, set)
class CollectionSerializer(AbstractCollectionSerializer):

    def encode_element(self, collection, item):
        if isinstance(item, list):
            if self.is_self(collection, item):
                return "[...]"

            self.set_parent(item, collection)

        return self.serialize_inner(item)

    def encode_collection(self, collection):
        return [
            self.encode_element(collection, item)
            for item in collection
        ]


@registry.register_class(dict)
class DictionarySerializer(AbstractCollectionSerializer):

    def encode_element(self, collection, item):
        if isinstance(item, dict):
            if self.is_self(collection, item):
                return "{...}"

            self.set_parent(item, collection)

        return self.serialize_inner(item)

    def encode_collection(self, dctx):
        return {
            self.serialize_inner(key): self.encode_element(dctx, dctx[key])
            for key in dctx
        }
