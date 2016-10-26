from collections import OrderedDict

from pytrace.conf import settings
from pytrace.core.debugger import ManagedDebugger, DebuggerEvent
from pytrace.serializers import ObjectSerializer
from pytrace.tracer import utils


class AbstractTraceRecorder(object):

    stack = None
    current_index = 0
    current_line_number = 0

    def __init__(self, serializer=None):
        if serializer is None:
            serializer = ObjectSerializer()

        self._debugger = ManagedDebugger(self._debugger_trigger)
        self._serializer = serializer
        self._initialize()

    def _initialize(self):
        self._traces = []
        self._global_funcs = set()
        self._frame_ordered_ids = {}
        self._closer_parents = {}
        self._current_frame_id = 1

    def _debugger_trigger(self, event, **kwargs):
        self._serializer.reset()
        frame = kwargs.get('frame', None)
        if frame:
            traceback = kwargs.get('traceback', None)
            kwargs['top_frame'] = self._walk_frame(event, frame, traceback)

        event_data = {}  # base_trigger(event, *args, **kwargs)
        self._encode_frame(event, event_data, kwargs.get('top_frame', None))
        return event_data

    def _walk_frame(self, event, frame, tb):
        self.stack, self.current_index = self._debugger.get_stack(frame, tb)
        top_frame, self.current_line_number = self.stack[self.current_index]

        if event == DebuggerEvent.EnterBlock:
            self._frame_ordered_ids[top_frame] = self._current_frame_id
            self._current_frame_id += 1

        if self.current_index > 1:
            self._extract_closure_parents(top_frame)
        else:
            self._extract_global_funcs(top_frame)

        return top_frame

    def _encode_frame(self, event, data, top_frame=None):

        if top_frame is None:
            encoded_frame = {}
        else:
            encoded_frame = self._encode_top_frame(top_frame)
            if encoded_frame is None:
                return

        encoded_frame['output'] = self._debugger.stdout
        encoded_frame['event'] = event
        encoded_frame['eventData'] = data
        encoded_frame['lineNumber'] = self.current_line_number
        self._traces.append(encoded_frame)

    def _encode_top_frame(self, top_frame):
        encoded_stack = []

        i = self.current_index
        current_frame = self.stack[i][0]

        while current_frame and current_frame.f_code.co_name != '<module>':
            if current_frame in self._frame_ordered_ids:
                encoded_stack.append(self._encode_stack_frame(current_frame))

            i -= 1
            current_frame = self.stack[i][0]

        frame_globals = utils.get_user_globals(top_frame)
        encoded_gloabls = OrderedDict()

        for k in frame_globals:
            encoded_gloabls[k] = self._serializer.encode(frame_globals[k])

        return {
            'name': top_frame.f_code.co_name,
            'stack': encoded_stack,
            'heap': self._serializer.heap.get_variables(),
            'globals': encoded_gloabls
        }

    def _encode_stack_frame(self, frame):
        frame_name = frame.f_code.co_name
        if not frame_name:
            frame_name = settings.UNKNOWN_FUNCTION

        frame_locals = utils.get_user_locals(frame)
        encoded_locals = {}

        for k in frame_locals:
            encoded_locals[k] = self._serializer.encode(frame_locals[k])

        ordered_locals = OrderedDict()
        for e in frame.f_code.co_varnames:
            if e in encoded_locals:
                ordered_locals[e] = encoded_locals[e]

        for e in sorted(encoded_locals.keys()):
            for k in ordered_locals:
                if k == e:
                    continue

                ordered_locals[e] = encoded_locals[e]

        return {
            'name': frame_name,
            'locals': ordered_locals,
            'uid': self.get_frame_id(frame)
        }

    def _extract_closure_parents(self, frame):
        for closure in utils.extract_frame_closures(frame):
            if (closure in self._closer_parents or
               closure in self._global_funcs):
                continue

            parent_frame = utils.find_closure_owner_frame(self.stack, closure)
            if parent_frame in self._frame_ordered_ids:
                self._closer_parents[closure] = parent_frame
                frame_name = parent_frame.f_code.co_name
                closure.__parent__ = closure.func_globals.get(frame_name, None)

    def _extract_global_funcs(self, frame):
        user_globals = utils.get_user_globals(frame)
        for k in user_globals:
            var = user_globals[k]
            if type(var) in utils.FUNCTION_TYPES and \
               var not in self._closer_parents:
                self._global_funcs.add(var)

    def get_frame_id(self, frame):
        return self._frame_ordered_ids[frame]

    def get_func_parent_frame_id(self, func):
        if func not in self._global_funcs:
            return None

        return self.get_frame_id(self._closer_parents[func])

    def run(self, script, input_queue=None):
        self._initialize()
        self._serializer.heap.clear()
        self._debugger.run(script, input_queue)
        return {
            'scriptLines': self._debugger.script_lines,
            'refs': self._serializer.heap.get_constants(),
            'steps': self._traces
        }

    def normalize_return_after_exception(self):
        if self._traces[-2]['event'] != DebuggerEvent.Exception:
            return

        last_trace = self._traces[-1]
        if (last_trace['event'] == DebuggerEvent.ExitBlock and
           last_trace['function'] == '<module>'):
            self._traces.pop()

    def normalize(self):
        if len(self._traces) >= 2:
            self.normalize_return_after_exception()
