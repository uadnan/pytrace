

class SerializerRegistry(object):
    """
    Holds serializers along with type as key value pair.
    Also provides methods & decorater to register serializer
    """

    def __init__(self):
        self._handlers = {}
        self._default = None

    def register(self, type_, serializer):
        """ Register serializer for specific type """
        if type_ in self._handlers:
            if serializer == self._handlers[type_]:
                return

            raise ValueError("A hanlder for `%s` already exists" % type_.__name__)

        self._handlers[type_] = serializer

    def register_many(self, types, func):
        """ Register single serializer for multiple types """
        if len(types) == 0:
            raise ValueError("Provide atleat one type handled by serializer")

        for type_ in types:
            self.register(type_, func)

    def register_class(self, *types):
        """
        Decorate to register class as serializer for specified types.
        Class will be lazy initialized and only instance will be for
        all given types
        """
        def register_handler(cls):
            self.register_many(types, cls)
            return cls

        return register_handler

    def default(self, cls):
        """
        Decorate to register default serializer. Class will be lazy initialized
        and only instance will be for all given types
        """
        self._default = cls
        return cls

    def get(self, type_, fallback=None):
        """
        Returns serializer for specified type if there is any otherwise
        returns `fallback` value as passed
        """
        if type_ in self._handlers:
            return self._handlers[type_]

        return fallback if fallback is not None else self._default


default = SerializerRegistry()
