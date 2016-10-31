import unittest2
import inspect

from pytrace.core.debugger import ManagedDebugger, DebuggerEvent


TEST_FUNCTION_SCRIPT = """
def hello(arg1, arg2, *args, **kwargs):
    var1 = 20
    return var1

hello(1, 2, 3, 4, 5, 6, x=1, y=3)
"""


class ManagedDebuggerTests(unittest2.TestCase):

    debugger_events = []

    def _debugger_step(self, event, *args, **kwargs):
        self.debugger_events.append((event, args, kwargs))

    def test_hello_world(self):
        self.debugger_events = []
        debugger = ManagedDebugger(self._debugger_step)
        debugger.run("print ('Hello Wolrd')")
        assert len(self.debugger_events) == 2

    def test_syntax_error(self):
        self.debugger_events = []
        debugger = ManagedDebugger(self._debugger_step)
        debugger.run("print 'Hello Wolrd")
        assert len(self.debugger_events) == 1
        assert self.debugger_events[0][0] == DebuggerEvent.SyntaxError
        assert isinstance(self.debugger_events[0][2]["exception"], SyntaxError)

    def test_step_line(self):
        self.debugger_events = []
        debugger = ManagedDebugger(self._debugger_step)
        debugger.run("print ('Hello Wolrd')")
        assert len(self.debugger_events) == 2
        assert self.debugger_events[0][0] == DebuggerEvent.StepLine

    def test_function_call(self):
        self.debugger_events = []
        debugger = ManagedDebugger(self._debugger_step)
        debugger.run(TEST_FUNCTION_SCRIPT)
        assert len(self.debugger_events) > 3
        assert self.debugger_events[2][0] == DebuggerEvent.EnterBlock

    def test_function_exit(self):
        self.debugger_events = []
        debugger = ManagedDebugger(self._debugger_step)
        debugger.run(TEST_FUNCTION_SCRIPT)
        assert len(self.debugger_events) > 5
        assert self.debugger_events[5][0] == DebuggerEvent.ExitBlock

    def test_return_value(self):
        self.debugger_events = []
        debugger = ManagedDebugger(self._debugger_step)
        debugger.run(TEST_FUNCTION_SCRIPT)
        assert len(self.debugger_events) > 5
        assert self.debugger_events[5][0] == DebuggerEvent.ExitBlock

        kwargs = self.debugger_events[5][2]
        assert 'return_value' in kwargs
        assert kwargs['return_value'] == 20

    def test_function_arguments_capturing(self):
        self.debugger_events = []
        debugger = ManagedDebugger(self._debugger_step)
        debugger.run(TEST_FUNCTION_SCRIPT)
        assert len(self.debugger_events) > 3
        arguments = self.debugger_events[2][2]['arguments']
        assert len(arguments) == 4
        assert 'arg1' in arguments
        assert 'arg2' in arguments
        assert 'args' in arguments
        assert 'kwargs' in arguments

        assert arguments['arg1'] == 1
        assert arguments['arg2'] == 2
        assert arguments['args'] == (3, 4, 5, 6)
        assert arguments['kwargs'] == dict(x=1, y=3)

    def test_exception(self):
        self.debugger_events = []
        debugger = ManagedDebugger(self._debugger_step)
        debugger.run("raise ValueError()")
        assert len(self.debugger_events) == 3
        assert self.debugger_events[1][0] == DebuggerEvent.Exception
        kwargs = self.debugger_events[1][2]

        assert 'frame' in kwargs
        assert 'ex_type' in kwargs
        assert 'traceback' in kwargs

        assert isinstance(kwargs['ex_type'], type)
        assert inspect.istraceback(kwargs['traceback'])
        assert inspect.isframe(kwargs['frame'])
