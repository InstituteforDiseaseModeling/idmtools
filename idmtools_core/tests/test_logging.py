import io
import os
import re
import sys
import tempfile
import unittest.mock
from idmtools import IdmConfigParser
from idmtools.core.platform_factory import Platform

from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from tests import logger_demo


class TestConfig(ITestWithPersistence):

    def setUp(self):
        super().setUp()
        self.platform = Platform('BAYESIAN')
        IdmConfigParser.clear_instance()
        self.case_name = self._testMethodName
        if os.path.exists(f"{self.case_name}.log"):
            os.remove(f"{self.case_name}.log")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_root_level_with_default_file_level_log(self, mock_stdout):
        ini_content = f"""
        [Logging]
            level = ERROR
            filename ={self.case_name}.log
        """
        f = self.create_temp_ini(ini_content)
        IdmConfigParser(file_name=f.name)

        sys.stdout = mock_stdout
        logger_demo.write_some_logs(user=True, root=True, comps=True, exp=True, full=False, check=False)

        with open(f"{self.case_name}.log", "r") as log_file_fd:
            log_file_content = log_file_fd.read()
            # validate root should be ERROR and above. user should be DEBUG and above
            matched = re.compile(r"write_some_logs \[ERROR\] \([0-9]+,[0-9]+\) - root: 4").search(log_file_content)
            self.assertTrue(bool(matched))
            matched = re.compile(r"write_some_logs \[CRITICAL\] \([0-9]+,[0-9]+\) - root: 5").search(log_file_content)
            self.assertTrue(bool(matched))
            matched = re.compile(r"write_some_logs \[DEBUG\] \([0-9]+,[0-9]+\) - root: 1").search(log_file_content)
            self.assertFalse(bool(matched))  # no debug root
            matched = re.compile(r"write_some_logs \[INFO\] \([0-9]+,[0-9]+\) - root: 2").search(log_file_content)
            self.assertFalse(bool(matched))  # no info root
            matched = re.compile(r"write_some_logs \[WARNING\] \([0-9]+,[0-9]+\) - root: 3").search(log_file_content)
            self.assertFalse(bool(matched))  # no warning root
            matched = re.compile(r"write_some_logs \[DEBUG\] \([0-9]+,[0-9]+\) - user: 11").search(log_file_content)
            self.assertTrue(bool(matched))
            matched = re.compile(r"write_some_logs \[INFO\] \([0-9]+,[0-9]+\) - user: 22").search(log_file_content)
            self.assertTrue(bool(matched))
            matched = re.compile(r"write_some_logs \[WARNING\] \([0-9]+,[0-9]+\) - user: 33").search(log_file_content)
            self.assertTrue(bool(matched))
            matched = re.compile(r"write_some_logs \[ERROR\] \([0-9]+,[0-9]+\) - user: 44").search(log_file_content)
            self.assertTrue(bool(matched))
            matched = re.compile(r"write_some_logs \[CRITICAL\] \([0-9]+,[0-9]+\) - user: 55").search(log_file_content)
            self.assertTrue(bool(matched))

        stdout = mock_stdout.getvalue()
        self.validate_color_console(stdout)
        self.clean_up(f)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_root_level_file_level_log(self, mock_stdout):
        ini_content = f"""
        [Logging]
            level = INFO
            file_level=WARNING
            filename ={self.case_name}.log
        """
        f = self.create_temp_ini(ini_content)
        IdmConfigParser(file_name=f.name)

        sys.stdout = mock_stdout  # reset sys.stdout to default
        logger_demo.write_some_logs(user=True, root=True, comps=True, exp=True, full=False, check=True)

        with open(f"{self.case_name}.log", "r") as log_file_fd:
            log_file_content = log_file_fd.read()
            # validate root should be WARNING and above. user should be WARNING and above
            matched = re.compile(r"write_some_logs \[WARNING\] - root: 3").search(log_file_content)
            self.assertTrue(bool(matched))
            matched = re.compile(r"write_some_logs \[ERROR\] - root: 4").search(log_file_content)
            self.assertTrue(bool(matched))
            matched = re.compile(r"write_some_logs \[CRITICAL\] - root: 5").search(log_file_content)
            self.assertTrue(bool(matched))
            matched = re.compile(r"write_some_logs \[DEBUG\] - root: 1").search(log_file_content)
            self.assertFalse(bool(matched))  # no DEBUG for root
            matched = re.compile(r"write_some_logs \[INFO\] - root: 2").search(log_file_content)
            self.assertFalse(bool(matched))  # no INFO for root

            matched = re.compile(r"write_some_logs \[DEBUG\] - user: 11").search(log_file_content)
            self.assertFalse(bool(matched))  # no DEBUG for user
            matched = re.compile(r"write_some_logs \[INFO\] - user: 22").search(log_file_content)
            self.assertFalse(bool(matched))  # no INFO for user
            matched = re.compile(r"write_some_logs \[WARNING\] - user: 33").search(log_file_content)
            self.assertTrue(bool(matched))
            matched = re.compile(r"write_some_logs \[ERROR\] - user: 44").search(log_file_content)
            self.assertTrue(bool(matched))
            matched = re.compile(r"write_some_logs \[CRITICAL\] - user: 55").search(log_file_content)
            self.assertTrue(bool(matched))

        stdout = mock_stdout.getvalue()
        self.validate_color_console(stdout)
        self.clean_up(f)


    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_console_on_log_off(self, mock_stdout):
        ini_content = f"""
        [Logging]
            console = on
            enable_file_logging = off
            filename ={self.case_name}.log
        """
        f = self.create_temp_ini(ini_content)
        IdmConfigParser(file_name=f.name)

        sys.stdout = mock_stdout
        logger_demo.write_some_logs(user=True, root=True, comps=True, exp=True, full=False, check=False)
        # validate no log file generate
        self.assertFalse(os.path.exists(f"{self.case_name}.log"))

        stdout = mock_stdout.getvalue()
        self.validate_default_user_console_on(stdout)
        self.clean_up(f)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_console_off_log_off(self, mock_stdout):
        ini_content = f"""
        [Logging]
            console = off
            enable_file_logging = off
            filename ={self.case_name}.log
        """
        f = self.create_temp_ini(ini_content)
        IdmConfigParser(file_name=f.name)

        sys.stdout = mock_stdout
        logger_demo.write_some_logs(user=True, root=True, comps=True, exp=True, full=False, check=False)
        # validate no log file generate
        self.assertFalse(os.path.exists(f"{self.case_name}.log"))

        stdout = mock_stdout.getvalue()
        self.validate_default_user_console_off(stdout)
        self.clean_up(f)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_console_on_user_output_on(self, mock_stdout):
        ini_content = f"""
        [Logging]
            level = CRITICAL
            console = on
            enable_file_logging = off
            user_output = on
        """
        f = self.create_temp_ini(ini_content)
        IdmConfigParser(file_name=f.name)

        sys.stdout = mock_stdout
        logger_demo.write_some_logs(user=True, root=True, comps=True, exp=True, full=False, check=False)
        self.assertFalse(os.path.exists(f"{self.case_name}.log"))

        stdout = mock_stdout.getvalue()
        matched = re.compile(r"CRITICAL.*root: 5").search(stdout)
        self.assertTrue(bool(matched))
        matched = re.compile(r"CRITICAL.*user: 55").search(stdout)
        self.assertTrue(bool(matched))
        self.clean_up(f)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_console_off_user_output_on(self, mock_stdout):
        ini_content = f"""
        [Logging]
            level = CRITICAL
            console = off
            enable_file_logging = off
            user_output = on
            use_colored_logs = on
        """
        f = self.create_temp_ini(ini_content)
        IdmConfigParser(file_name=f.name)

        sys.stdout = mock_stdout
        logger_demo.write_some_logs(user=True, root=True, full=False, check=True)
        self.assertFalse(os.path.exists(f"{self.case_name}.log"))

        stdout = mock_stdout.getvalue()
        self.validate_color_console(stdout)
        self.clean_up(f)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_use_colored_logs_off(self, mock_stdout):
        ini_content = f"""
        [Logging]
            console = off
            enable_file_logging = off
            user_output = on
            use_colored_logs = off
        """
        f = self.create_temp_ini(ini_content)
        IdmConfigParser(file_name=f.name)

        logger_demo.write_some_logs(user=True, root=True, check=True)
        self.assertFalse(os.path.exists(f"{self.case_name}.log"))

        stdout = mock_stdout.getvalue()
        self.validate_default_user_console_off(stdout)
        self.clean_up(f)

    def validate_default_user_console_off(self, stdout):
        matched = re.compile(r"user: 11").search(stdout)
        self.assertFalse(bool(matched))  # should not print debug user, since user is VERBOSE now
        matched = re.compile(r"user: 22").search(stdout)
        self.assertTrue(bool(matched))
        matched = re.compile(r"user: 33").search(stdout)
        self.assertTrue(bool(matched))
        matched = re.compile(r"user: 44").search(stdout)
        self.assertTrue(bool(matched))
        matched = re.compile(r"user: 55").search(stdout)
        self.assertTrue(bool(matched))

    def validate_color_console(self, stdout):
        matched = re.compile(r"user: 11").search(stdout)
        self.assertFalse(bool(matched))  # should not print debug user, since user is VERBOSE now
        matched = re.compile(r"user: 22").search(stdout)
        self.assertTrue(bool(matched))
        matched = re.compile(r"33muser: 33").search(stdout)
        self.assertTrue(bool(matched))
        matched = re.compile(r"31muser: 44").search(stdout)
        self.assertTrue(bool(matched))
        matched = re.compile(r"1;31muser: 55").search(stdout)
        self.assertTrue(bool(matched))

    def validate_default_user_console_on(self, stdout):
        matched = re.compile(r"WARNING.*root: 3").search(stdout)
        self.assertTrue(bool(matched))
        matched = re.compile(r"ERROR.*root: 4").search(stdout)
        self.assertTrue(bool(matched))
        matched = re.compile(r"CRITICAL.*root: 5").search(stdout)
        self.assertTrue(bool(matched))
        matched = re.compile(r"WARNING.*user: 33").search(stdout)
        self.assertTrue(bool(matched))
        matched = re.compile(r"ERROR.*user: 44").search(stdout)
        self.assertTrue(bool(matched))
        matched = re.compile(r"CRITICAL.*user: 55").search(stdout)
        self.assertTrue(bool(matched))

    def create_temp_ini(self, ini_str):
        f = tempfile.NamedTemporaryFile(mode='wb', delete=False)
        f.write(ini_str.replace("\r", "").encode('utf-8'))
        f.flush()
        return f

    def clean_up(self, f):
        f.close()
        os.remove(f.name)   # delete temp ini file