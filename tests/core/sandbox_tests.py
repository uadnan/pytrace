import unittest2
import pkg_resources

from pytrace.conf import settings
from pytrace.core.sandbox import Sandbox
from pytrace.core.exceptions import UnsafeImportError


class SandboxTests(unittest2.TestCase):

    def test_hello_world(self):
        sandbox = Sandbox()
        sandbox.run("print ('Hello Wolrd')")

    def test_safe_import(self):
        sandbox = Sandbox()
        for module_name in settings.SAFE_MODULES:
            sandbox.run("import %s" % module_name)

    def test_safe_import_non_str(self):
        sandbox = Sandbox()
        self.assertRaises(TypeError, sandbox.run, "__import__([])")

    def test_unsafe_import(self):
        sandbox = Sandbox()
        for module_name in pkg_resources.__dict__:
            if module_name in settings.SAFE_MODULES:
                continue

            self.assertRaises(UnsafeImportError, sandbox.run, "import %s" % module_name)

    def test_unsafe_builtins(self):
        sandbox = Sandbox()
        for name in settings.UNSAFE_BUILTINS:
            self.assertRaises(NameError, sandbox.run, name)

    def test_stdout(self):
        old_redirect_stdout = settings.REDIRECT_STDOUT
        settings.REDIRECT_STDOUT = True
        try:
            sandbox = Sandbox()
            sandbox.run('print ("Hello World")')
            assert sandbox.stdout == "Hello World\n"
        finally:
            settings.REDIRECT_STDOUT = old_redirect_stdout

    def test_system_exit(self):
        sandbox = Sandbox()
        sandbox.run('raise SystemExit()')
