"""
Python Sandbox
"""
import sys
from collections import deque as Queue
from six import StringIO, exec_

from pytrace.conf import settings
from pytrace.core.builtins import builtins


def default_runner(script, user_globals, user_locals):
    exec_(script, user_globals, user_locals)


class Sandbox(object):
    """
    Restricts execution of unsafe code and manages output streams
    """

    def _initialize(self, inputs):

        if inputs is None:
            inputs = []

        assert isinstance(inputs, (list, tuple)), "inputs must be list or tuple"  # NOQA

        self._raw_stdout = sys.stdout
        self._raw_stderr = sys.stderr

        self._stdout = None
        if settings.REDIRECT_STDERR or settings.REDIRECT_STDOUT:
            self._stdout = StringIO()

        if settings.REDIRECT_STDOUT:
            sys.stdout = self._stdout

        if settings.REDIRECT_STDERR:
            sys.stderr = self._stdout

        settings.INPUT_QUEUE = Queue(inputs)
        self._locals = {
            '__name__': '__pytrace__',
            '__builtins__': builtins.allowed()
        }

    @property
    def stdout(self):
        if settings.REDIRECT_STDERR or settings.REDIRECT_STDOUT:
            return self._stdout.getvalue()

    def _finalizer(self):
        sys.stdout = self._raw_stdout
        sys.stderr = self._raw_stderr

    def run(self, script, input_queue=None, runner=None):
        if runner is None:
            runner = default_runner

        self._initialize(input_queue)
        try:
            runner(script, self._locals, self._locals)
        except SystemExit:
            pass
        finally:
            self._finalizer()
