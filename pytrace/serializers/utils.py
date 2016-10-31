

def get_object_name(obj):
    """ Get friendly name of object """
    if hasattr(obj, '__name__'):
        return obj.__name__

    return get_object_name(type(obj))
