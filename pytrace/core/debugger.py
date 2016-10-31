"""
Managed Python Debugger
"""

import re
import sys
import logging
import inspect

from bdb import Bdb
from enum import Enum

from pytrace.core.sandbox import Sandbox


CLASS_DEF_REGEX = re.compile('^\\s+class\\s+')
logger = logging.getLogger("pytrace")


def contains_class_defination(line):
    "Returns True if line contains class defination otherwise False"
    return CLASS_DEF_REGEX.match(line)


class DebuggerEvent(Enum):
    "Events triggered by `ManagedDebugger`"
    StepLine = 1            # Control jumped to next line
    EnterBlock = 2          # Control enters a code block
    ExitBlock = 3           # Control exits a code block
    Exception = 4           # Hanlded or Unhandled Exception occured
    SyntaxError = 5         # Syntax Error within executing script
    SystemError = 6         # Internal System Error while executing code


class ManagedDebugger(object):
    """ Managed Python Debugger """

    _wait_stack_height = 0
    _done = False
    _excep_logged = False
    _script_lines = []

    def __init__(self, action_handler, **kwargs):
        super(ManagedDebugger, self).__init__(**kwargs)
        self._bdb = Bdb()
        self._sandbox = Sandbox()
        self._handler = action_handler

        self._bdb.user_call = self._bdb_call
        self._bdb.user_line = self._bdb_line
        self._bdb.user_return = self._bdb_return
        self._bdb.user_exception = self._bdb_exception

    def _initialize(self):
        self._done = False
        self._excep_logged = False

        self._wait_stack_height = 0

    # bdb Callbacks
    def _bdb_call(self, frame, args):
        if self._done:
            return  # Execution is stopped

        if frame.f_code.co_filename != "<string>" or frame.f_lineno <= 0:
            self._wait_stack_height += 1
            return

        if self._wait_stack_height:
            self._wait_stack_height += 1
            return

        if not self._bdb.stop_here(frame):
            return

        script_line = self._get_script_line(frame.f_code.co_firstlineno)
        if contains_class_defination(script_line):
            self._wait_stack_height = 1
            return

        args = self._extract_passed_arguments(frame)
        self.trigger(DebuggerEvent.EnterBlock, frame=frame, arguments=args)

    def _extract_passed_arguments(self, frame):
        function = frame.f_globals[frame.f_code.co_name]
        arg_specs = inspect.getargspec(function)

        args = {
            arg: frame.f_locals[arg]
            for arg in arg_specs.args
        }

        if arg_specs.varargs:
            args[arg_specs.varargs] = frame.f_locals[arg_specs.varargs]

        if arg_specs.keywords:
            args[arg_specs.keywords] = frame.f_locals[arg_specs.keywords]

        return args

    def _bdb_line(self, frame):
        if self._done or self._wait_stack_height:
            return

        self._excep_logged = False
        self.trigger(DebuggerEvent.StepLine, frame=frame)

    def _bdb_return(self, frame, value):
        if self._done:
            return

        if self._wait_stack_height:
            self._wait_stack_height -= 1
        elif frame.f_code.co_filename == "<string>":
            self.trigger(DebuggerEvent.ExitBlock, frame=frame, return_value=value)

    def _bdb_exception(self, frame, info):
        if self._done or self._wait_stack_height:
            return

        self._excep_logged = True
        ex_type, value, tb = info

        self.trigger(DebuggerEvent.Exception, frame=frame, ex_type=ex_type,
                     value=value, traceback=tb)

    def trigger(self, event, *args, **kwargs):
        return self._handler(event, *args, **kwargs)

    def _get_script_line(self, n):
        return self.script_lines[n - 1]

    def get_stack(self, frame, tb):
        return self._bdb.get_stack(frame, tb)

    @property
    def stdout(self):
        return self._sandbox.stdout

    def run(self, script, input_queue=None):
        self._initialize()

        try:
            self.script_lines = script.splitlines()
            self._sandbox.run(script, input_queue, runner=self._bdb.run)
        except SyntaxError as ex:
            self.trigger(DebuggerEvent.SyntaxError, exception=ex)
        except:
            if not self._excep_logged:
                logger.exception(
                    "Internal Error in Debugger\n"
                    "Script:\n%s\n"
                    "Input Queue:%s",
                    script, input_queue
                )
                ex_type, value, tb = sys.exc_info()
                self.trigger(DebuggerEvent.SystemError, type=ex_type,
                             value=value, traceback=tb)
        finally:
            self._done = True
