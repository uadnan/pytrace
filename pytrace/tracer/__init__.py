from pytrace.conf import settings
from pytrace.tracer.base import AbstractTraceRecorder


class ControlledTraceRecorder(AbstractTraceRecorder):

    def __init__(self, max_steps=None):
        if max_steps is None:
            max_steps = settings.MAX_STEPS

        self._max_steps = max_steps
        super(ControlledTraceRecorder, self).__init__()

    def _encode_frame(self, event, data, top_frame=None):
        super(ControlledTraceRecorder, self). \
             _encode_frame(event, data, top_frame=top_frame)

        if len(self._traces) >= self._max_steps:
            self._traces.append(dict(
                event='overflow'
            ))
            raise SystemExit()
