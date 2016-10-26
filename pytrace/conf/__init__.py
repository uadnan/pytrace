"""
PyTrace Settings and configuration.

Default values will be read from pytrace.conf.global_settings;
see the global settings file for a list of all possible variables.
"""

# Taken from Django Framework (https://www.djangoproject.com)
# and modified based on usecase by Adnan Umer <u.adnan@outlook.com>
# See LICENSE.django for complete Django Framework license

from pytrace.conf import global_settings
from pytrace.utils.functional import LazyObject, empty
from pytrace.utils.module_loading import import_string


class LazySettings(LazyObject):
    """
    A lazy proxy for either global settings or a custom settings object.
    The user can manually configure settings prior to using them.
    """

    def _setup(self):
        """
        Load the pytrace.conf.global_settings. This is used the first time we
        need any settings at all, if the user has not previously configured
        the settings manually.
        """
        self._wrapped = Settings()

    def __getattr__(self, name):
        if self._wrapped is empty:
            self._setup()

        return getattr(self._wrapped, name)


class Settings(object):
    """
    Container to hold currently applicable settings.

    Initial values will be loaded from `pytrace.conf.global_settings` and
    later those values can be easily overriden at runtime

    Example of changing settings at runtime:
        > from pytrace.conf import settings
        > settings.DEBUG = True
    """

    def __init__(self):
        """
        Creates a new instance of `Settings` and loads all default settings from
        `pytrace.conf.global_settings`. Only ALL_CAPS settings will be loaded
        """
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))

    def from_object(self, settings_object):
        """
        Updates the values from the given object. An object can be of one
        of the following two types:
        -   a string: in this case the object with that name will be imported
        -   an actual object reference: that object is used directly

        Objects are usually either modules or classes. `from_object`
        loads only the uppercase attributes of the module/class. A ``dict``
        object will not work with `from_object` because the keys of a
        ``dict`` are not attributes of the ``dict`` class.

        Example of module-based configuration::
            > from pytrace.conf import settings
            > settings.from_object('yourapplication.default_config')

        Another example:
            > from pytrace.conf import settings
            > from yourapplication import default_config
            > settings.from_object(default_config)
        """
        if isinstance(settings_object, (str, unicode)):
            settings_object = import_string(settings_object)

        for key in dir(settings_object):
            if key.isupper():
                setattr(self, key, getattr(settings_object, key))


settings = LazySettings()
