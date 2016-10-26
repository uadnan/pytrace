"""
Global PyTrace exception classes.
"""


class ImproperlyConfigured(Exception):
    """PyTrace is somehow improperly configured"""
    pass


class StandardInputReadError(Exception):
    """
    Raised when attempted to read from Standard Input Stream
    while Input Queue is empty
    """

    MESSAGE = "Unable to read from Standard Input Steam"

    def __init__(self, prompt):
        super(StandardInputReadError, self).__init__(self.MESSAGE)
        self.prompt = prompt


class StandardInputEvalError(Exception):
    """
    Raised by `UserInputReader` when in evaluation mode and user input
    contains error
    """

    def __init__(self, real_exception=None):
        msg = None
        if isinstance(real_exception, SyntaxError):
            msg = real_exception.msg
            self.filename = real_exception.filename
            self.lineno = real_exception.lineno
            self.message = real_exception.message
            self.offset = real_exception.offset
        elif isinstance(real_exception, (str, unicode)):
            msg = real_exception

        super(StandardInputEvalError, self).__init__(msg)


class StandardInputError(Exception):
    """
    Warpper around exception raised by `exec` by `UserInputReader` when in
    evaluation mode
    """

    def __init__(self, inner_exception):
        super(StandardInputError, self).__init__(str(inner_exception))
        self.inner_exception = inner_exception


class UnsafeImportError(Exception):
    """
    Raised when attempted to import module that is not marked as safe within
    sandbox
    """

    message_format = "%s is not allowed to be imported in current environment"

    def __init__(self, module, *args):
        msg = self.message_format % module
        super(UnsafeImportError, self).__init__(msg, *args)


class NoSerializerFoundError(Exception):
    """
    Raised by `pytrace.serializers` when no suitable serializer is
    found for serialization
    """

    def __init__(self, value_type, *args):
        message = "No type serializer found for {0}".format(value_type)
        super(NoSerializerFoundError, self).__init__(message, *args)


class SerializationError(Exception):
    """
    Raised by `pytrace.serializers` when failed to encode specified value due
    to internal serializer error
    """

    def __init__(self, encoder, value, *args):
        self.encoder = encoder
        self.value = value

        message = "Failed to serialize {0} using {1}".format(value, encoder)
        super(SerializationError, self).__init__(message, *args)
