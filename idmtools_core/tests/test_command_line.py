import unittest
import allure
import pytest

from idmtools.entities import CommandLine


@pytest.mark.smoke
@pytest.mark.serial
@allure.suite("idmtools_core")
class TestCommandLine(unittest.TestCase):
    def test_quotes(self):
        cl = CommandLine('python36 Assets/examples.py "a b c"', is_windows=False)
        self.assertEqual("python36 Assets/examples.py 'a b c'", str(cl))
        cl.is_windows = True
        self.assertEqual("python36 Assets/examples.py \"a b c\"", str(cl))

    def test_quotes_raw(self):
        cl = CommandLine.from_string('python36 Assets/examples.py "a b c"', as_raw_args=True)
        self.assertEqual("python36 Assets/examples.py \"a b c\"", str(cl))
        cl.is_windows = True
        self.assertEqual("python36 Assets/examples.py \"a b c\"", str(cl))

    def test_wildcards_raw(self):
        cl = CommandLine('python36 Assets/examples.py', is_windows=False)
        cl.add_argument("--input")
        cl.add_argument("Ada Lovelace.MD")
        cl.add_raw_argument("--input-pattern")
        cl.add_raw_argument("\"**\"")
        self.assertEqual("python36 Assets/examples.py --input 'Ada Lovelace.MD' --input-pattern \"**\"", str(cl))
        cl.is_windows = True
        self.assertEqual("python36 Assets/examples.py --input \"Ada Lovelace.MD\" --input-pattern \"**\"", str(cl))

    def test_wildcards(self):
        cl = CommandLine('python36 Assets/examples.py', is_windows=False)
        cl.add_argument("--input")
        cl.add_argument("Ada Lovelace.MD")
        cl.add_argument("--input-pattern")
        cl.add_argument("**")
        self.assertEqual("python36 Assets/examples.py --input 'Ada Lovelace.MD' --input-pattern '**'", str(cl))
        cl.is_windows = True
        self.assertEqual("python36 Assets/examples.py --input \"Ada Lovelace.MD\" --input-pattern **", str(cl))

    def test_trailing(self):
        cl = CommandLine('python36 Assets/examples.py', is_windows=False)
        cl.add_argument("--input")
        cl.add_argument("Ada Lovelace.MD")
        cl.add_raw_argument("--input-pattern                           ")
        self.assertEqual("python36 Assets/examples.py --input 'Ada Lovelace.MD' --input-pattern", str(cl))
        cl.is_windows = True
        self.assertEqual("python36 Assets/examples.py --input \"Ada Lovelace.MD\" --input-pattern", str(cl))
