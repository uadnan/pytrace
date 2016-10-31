from pytrace.core.debugger import DebuggerEvent
from pytrace.dispatch import Signal


SIGNALS = {
    DebuggerEvent.StepLine: Signal(providing_args=["frame", "top_frame"]),
    DebuggerEvent.EnterBlock: Signal(providing_args=[
        "frame", "top_frame", "arguments"]),
    DebuggerEvent.ExitBlock: Signal(providing_args=["frame", "top_frame"]),
    DebuggerEvent.Exception: Signal(providing_args=[
        "frame", "top_frame", "ex_type", "value", "traceback"]),
    DebuggerEvent.SyntaxError: Signal(providing_args=["exception"]),
    DebuggerEvent.SystemError: Signal(providing_args=[
        "ex_type", "value", "traceback"]),
}
