import types

from pytrace import compat
from pytrace.conf import settings


FUNCTION_TYPES = (types.FunctionType, types.MethodType)
COLLECTION_TYPES = (list, tuple, set)


def is_class_or_instance(obj):
    return compat.is_class(obj) or compat.is_class_instance(obj)


def filter_vars_dict(vars_dict):
    """
    Removes all the IGNORE_VARS from variables dictionary
    Returns a new dictionary instead of altering existing.
    """
    filtered_vars = {}
    for k in vars_dict:
        if k not in settings.IGNORE_VARS:
            filtered_vars[k] = vars_dict[k]

    return filtered_vars


def get_user_locals(frame):
    """
    Returns list of non-ignored locals within specified frame
    """
    return filter_vars_dict(frame.f_locals)


def get_user_globals(frame):
    """
    Returns list of non-ignored globals within specified frame
    """
    return filter_vars_dict(frame.f_globals)


def extract_functions(obj):
    """
    Recursively find and yields all functions within specified object
    """
    object_type = type(obj)
    child_map = None

    if object_type in FUNCTION_TYPES:
        yield obj
    elif object_type in COLLECTION_TYPES:
        for ele in obj:
            for child in extract_functions(ele):
                yield child
    elif object_type == dict:
        child_map = obj
    elif is_class_or_instance(obj) and hasattr(obj, '__dict__'):
        child_map = obj.__dict__

    if child_map:
        for key in child_map:
            for child in extract_functions(key):
                yield child

            for child in extract_functions(child_map[key]):
                yield child


def extract_frame_closures(frame):
    """
    Recursively find and yields all functions within specified frame locals
    """
    frame_locals = get_user_locals(frame)
    for k in frame_locals:
        for child in extract_functions(frame_locals[k]):
            if child is not None:
                yield child


def find_closure_owner_frame(stack, closure):
    """
    Search for parent of closure inside given stack
    """
    for frame, _ in stack:
        for constant in frame.f_code.co_consts:
            if constant is closure.func_code:
                return frame
