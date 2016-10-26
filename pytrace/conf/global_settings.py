"""
Global Configurations for pytrace
"""
from collections import deque
from six import PY2

####################
# CORE             #
####################

DEBUG = False

# List of types to be interpreted as primitives
PRIMITIVE_TYPES = [
    int,
    float,
    complex,
    str,
    bytearray,
    bool,
    type(None)
]
if PY2:
    PRIMITIVE_TYPES.extend([long, unicode])
else:
    PRIMITIVE_TYPES.append(bytes)


####################
# SANDBOX          #
####################

REDIRECT_STDOUT = not DEBUG
REDIRECT_STDERR = not DEBUG

# List of allowed external modules
SAFE_MODULES = (
    'math',
    'random',
    're',
    'json',
    'itertools',
    'collections'
)

# List of all builtins that are unsafe
UNSAFE_BUILTINS = (
    'reload',
    'open',
    'compile',
    'file',
    'execfile',
    'exit',
    'quit',
    'help',
    'dir',
    'globals',
    'locals',
    'vars'
)

# User Inputs queue. Each call to `input` or `raw_input` will
# read value from this queue instead of Standard Input Stream
INPUT_QUEUE = deque()

####################
# RECORDER         #
####################

# Maximum execution steps to record.
# Any script that exceed this limit in term of execution
# setps will be forcefully stopped in order to prevent infinite
# loops or length programs.
MAX_STEPS = 500

# List of variables which will be excluded while serialization of
# class, instance or module attributes
IGNORE_VARS = (
    '__builtins__',
    '__name__',
    '__doc__',
    '__package__',
    '__author__',
    '__module__'
)

# Fallback function name to use when failed to find function name
UNKNOWN_FUNCTION = '<<Unnamed Function>>'
