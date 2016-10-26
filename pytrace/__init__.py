"""
PyTrace - Python Execution Tracer
"""


def setup():
    """
    Configure the settings
    """
    from pytrace.conf import settings
    settings._setup()


setup()
