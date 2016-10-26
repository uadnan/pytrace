"""
Wrapper around unsafe builtins like (input, raw_input, import)
to make them work within sandbox without any potential harm.
"""

import ast
import inspect
import six

from pytrace.conf import settings
from pytrace.core.exceptions import (
    StandardInputReadError, StandardInputEvalError, UnsafeImportError
)

from pytrace.utils.functional import Singleton


@six.add_metaclass(Singleton)
class Builtins(object):

    def __init__(self):
        self._overrides = {}

    def override(self, name, *args, **kwargs):

        def inner(cls):
            value = cls
            if inspect.isclass(value):
                value = value(*args, **kwargs)

            self._overrides[name] = value
            return cls

        return inner

    def is_overridden(self, name):
        return name in self._overrides

    def get_override(self, name):
        return self._overrides[name]

    def filter(self, all_builtins):
        """
        Filters all unsafe builtins from given dictionary of all
        builtins and returns a new dictionary of safe builtins.

        For complete list of all unsafe builtins see
        `pytrace.conf.settings.UNSAFE_BUILTINS`
        """
        builtins = {}

        for k, v in all_builtins:
            if k in settings.UNSAFE_BUILTINS:
                continue

            if self.is_overridden(k):
                v = self.get_override(k)

            builtins[k] = v

        return builtins

    def all(self):
        "Return dictionary of all available builtins"
        builtins = __builtins__
        if hasattr(builtins, '__dict__'):
            builtins = builtins.__dict__

        return builtins.items()

    def allowed(self):
        """
        Returns dictionary of all allowed safe builtins including
        mocked builtins i.e. input, __import__ etc
        """
        return self.filter(self.all())


builtins = Builtins()


@six.add_metaclass(Singleton)
class BuiltinBase(object):
    "Base class for all mocked builtins"

    def __init__(self, actual_builtin):
        self.__doc__ = actual_builtin.__doc__
        self.__name__ = actual_builtin.__name__


class InputFunction(BuiltinBase):
    """
    Mock implementation of `input` and `raw_input`.

    Instead of reading inputs from standard input stream, this
    implementation uses `pytrace.conf.settings.INPUT_QUEUE`. Any
    call will dequeue an item from queue and if `evaluate` is set
    value will be first passed to `ast.literal_eval` rather then to
    `eval` (to disable execution of unsafe code) and results will
    be returned. If queue is empty this will throw `StandardInputReadError`
    """

    def __init__(self, evaluate=False):
        if not six.PY2 and evaluate:
            raise ValueError(
                "evaluate can only be set to True for Python 2.X as "
                "alternative to `input`"
            )

        actual_builtin = input
        if six.PY2 and not evaluate:
            actual_builtin = raw_input

        super(InputFunction, self).__init__(actual_builtin)
        self._eval = evaluate

    def __call__(self, prompt=None, *args, **kwargs):
        """
        Returned next element from undelaying queue. If queue is
        empty, StandardInputReadError will be raised.

        If `evaluate` flag is set, only literals will be evaluated,
        In case of eval failure, StandardInputEvalError will be raised
        """
        if len(settings.INPUT_QUEUE) == 0:
            raise StandardInputReadError(prompt=prompt)

        value = str(settings.INPUT_QUEUE.pop())
        if self._eval:
            try:
                return ast.literal_eval(value)
            except SyntaxError as ex:
                raise StandardInputEvalError(ex)
            except ValueError as ex:
                raise StandardInputEvalError(str(ex))

        return value

if six.PY2:
    builtins.override('raw_input')(InputFunction)
    builtins.override('input', evaluate=True)(InputFunction)
else:
    builtins.override('input')(InputFunction)


@builtins.override('__import__')
class ImportStatement(BuiltinBase):
    """
    Wrapper around __import__ builtin to allow only importing of
    safe modules

    For complete list of safe modules see `pytrace.conf.settings.SAFE_MODULES`
    """

    def __init__(self):
        BuiltinBase.__init__(self, __import__)

    def __call__(self, module, *args):
        if module in settings.SAFE_MODULES:
            return __import__(module, *args)

        if not isinstance(module, str):
            raise TypeError(
                "__import__() argument 1 must be string, "
                "not %s" % type(module).__name__
            )

        raise UnsafeImportError(module)
