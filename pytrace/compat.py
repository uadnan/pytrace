import re
import types
import inspect
import six

from pytrace.conf import settings


if six.PY3:
    TypeType = type

    def get_func_code(func):
        return func.__code__

    def get_im_class(method):
        if inspect.ismethod(method):
            for cls in inspect.getmro(method.__self__.__class__):
                if cls.__dict__.get(method.__name__) is method:
                    return cls

            method = method.__func__  # fallback to __qualname__ parsing

        if inspect.isfunction(method):
            class_name = method.__qualname__.split('.<locals>', 1)[0] \
                            .rsplit('.', 1)[0]

            cls = getattr(inspect.getmodule(method), class_name)
            if isinstance(cls, type):
                return cls

    def is_class_instance(obj):
        return type(obj) not in settings.PRIMITIVE_TYPES and \
               isinstance(type(obj), type) and \
               not isinstance(obj, type)

    def is_lambda(obj):
        if hasattr(obj, '__name__'):
            return obj.__name__ == '<lambda>'

        return False

    def is_class(obj):
        return isinstance(obj, type)

else:
    TypeType = types.TypeType

    def get_func_code(func):
        return func.func_code

    def get_im_class(method):
        return method.im_class

    TYPE_RE = re.compile("<type '(.*)'>")

    def is_class_instance(obj):
        return isinstance(obj, types.InstanceType) or \
               TYPE_RE.match(str(type(obj)))

    def is_lambda(obj):
        if hasattr(obj, 'func_name'):
            return obj.func_name == '<lambda>'

        return False

    def is_class(obj):
        return isinstance(obj, (types.ClassType, types.TypeType))
