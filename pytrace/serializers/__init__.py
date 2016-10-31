"""
Type serializers
"""

import os.path
import importlib
import pkgutil

from .base import ObjectSerializer  # NOQA

CURRENT_DIR = os.path.dirname(__file__)

# Import all files within current package to make sure all
# serializer got chance to register itself before anything else
for (_, name, _) in pkgutil.iter_modules([CURRENT_DIR]):
    importlib.import_module('.' + name, __package__)
