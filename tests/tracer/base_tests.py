import unittest2

from pytrace.tracer.base import AbstractTraceRecorder


class SerializerTestCase(unittest2.TestCase):

    def test_hello_world(self):
        recorder = AbstractTraceRecorder()
        recorder.run("print ('Hello World')")
