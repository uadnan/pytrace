import types

from six import PY2
from pytrace.core.builtins import BuiltinBase
from pytrace import compat


CONSTANT_TYPES = [
    int,
    float,
    complex,
    str,
    bool,
    frozenset,

    types.BuiltinFunctionType,
    types.BuiltinMethodType,

    compat.TypeType,
    tuple,

    types.FunctionType,
    types.MethodType
]

if PY2:
    CONSTANT_TYPES.extend([long, unicode])
else:
    CONSTANT_TYPES.append(bytes)


def is_constant(type_):
    """
    Returns wheather specific type_ is immutable
    """
    return type_ in CONSTANT_TYPES or BuiltinBase in type.mro(type_)


class Heap(object):
    """
    Heap memory representation. Assign arbitrary address to stored objects.
    """

    def __init__(self):
        self.clear()
        self.reset()

    def get_variables(self):
        return dict(self._variables)

    def get_constants(self):
        return dict(self._consts)

    def clear(self):
        self._consts = {}
        self._id_mappings = {}
        self._seed = 1

    def reset(self):
        self._variables = {}

    def __getitem__(self, key):
        if key in self._consts:
            return self._consts[key]

        return self._variables[key]

    def __len__(self):
        return len(self._variables) + len(self._consts)

    def store(self, encoded_value, actual_value=None):
        """
        Assign a unique arbirary number as address to object,
        store that against that number and return unique number.
        """
        if actual_value is None:
            actual_value = encoded_value

        obj_id = id(actual_value)
        fake_id = hex(self._seed)

        if obj_id in self._id_mappings:
            fake_id = self._id_mappings[obj_id]
            if fake_id in self._variables or fake_id in self._consts:
                return fake_id

        self._id_mappings[obj_id] = fake_id
        if is_constant(type(actual_value)):
            self._consts[fake_id] = encoded_value
        else:
            self._variables[fake_id] = encoded_value

        self._seed += 1
        return fake_id
