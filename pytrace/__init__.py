"""
PyTrace - Python Execution Tracer
"""

__author__ = "Adnan Umer"
__version__ = "0.0.1a1"


def setup():
    """
    Configure the settings
    """
    from pytrace.conf import settings
    settings._setup()


setup()

from pytrace.tracer import ControlledTraceRecorder, AbstractTraceRecorder


def trace(script, input_queue=None, tracer_class=ControlledTraceRecorder, **options):
    assert issubclass(tracer_class, AbstractTraceRecorder)
    tracer = tracer_class(**options)
    return tracer.run(script, input_queue=input_queue)
