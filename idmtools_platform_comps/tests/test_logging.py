import io
import os
import re
import sys
import tempfile
import unittest.mock
from contextlib import suppress

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
        self.tempfile_ini = None
        if os.path.exists(f"{self.case_name}.log"):
            os.remove(f"{self.case_name}.log")

    def tearDown(self):
        super().tearDown()

        try:
            if self.tempfile_ini:
                self.tempfile_ini.close()
                os.remove(self.tempfile_ini.name)
            with suppress(PermissionError):
                if os.path.exists(f"{self.case_name}.log"):
                    os.remove(f"{self.case_name}.log")
        finally:
            pass

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_root_level_with_default_file_level_log(self, mock_stdout):
        ini_content = f"""
        [Logging]
            level = ERROR
            filename ={self.case_name}.log
        """
        self.create_temp_ini(ini_content)
        IdmConfigParser(file_name=self.tempfile_ini.name)

        sys.stdout = mock_stdout
        logger_demo.write_some_logs(user=True, root=True, comps=True, exp=True, full=False, check=False)

        with open(f"{self.case_name}.log", "r") as log_file_fd:
            log_file_content = log_file_fd.read()
            # validate root should be ERROR and above. user should be DEBUG and above
            matched = re.search(r"write_some_logs \[ERROR\] \([0-9]+,[0-9]+\) - root: 4", log_file_content)
            self.assertTrue(matched)
            matched = re.search(r"write_some_logs \[CRITICAL\] \([0-9]+,[0-9]+\) - root: 5", log_file_content)
            self.assertTrue(matched)
            matched = re.search(r"write_some_logs \[DEBUG\] \([0-9]+,[0-9]+\) - root: 1", log_file_content)
            self.assertFalse(bool(matched))  # no debug root
            matched = re.search(r"write_some_logs \[INFO\] \([0-9]+,[0-9]+\) - root: 2", log_file_content)
            self.assertFalse(bool(matched))  # no info root
            matched = re.search(r"write_some_logs \[WARNING\] \([0-9]+,[0-9]+\) - root: 3", log_file_content)
            self.assertFalse(bool(matched))  # no warning root
            matched = re.search(r"write_some_logs \[DEBUG\] \([0-9]+,[0-9]+\) - user: 11", log_file_content)
            self.assertTrue(matched)
            matched = re.search(r"write_some_logs \[INFO\] \([0-9]+,[0-9]+\) - user: 22", log_file_content)
            self.assertTrue(matched)
            matched = re.search(r"write_some_logs \[WARNING\] \([0-9]+,[0-9]+\) - user: 33", log_file_content)
            self.assertTrue(matched)
            matched = re.search(r"write_some_logs \[ERROR\] \([0-9]+,[0-9]+\) - user: 44", log_file_content)
            self.assertTrue(matched)
            matched = re.search(r"write_some_logs \[CRITICAL\] \([0-9]+,[0-9]+\) - user: 55", log_file_content)
            self.assertTrue(matched)
            log_file_fd.close()

        stdout = mock_stdout.getvalue()
        self.validate_color_console(stdout)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_root_level_file_level_log(self, mock_stdout):
        ini_content = f"""
        [Logging]
            level = INFO
            file_level=WARNING
            filename ={self.case_name}.log
        """
        self.create_temp_ini(ini_content)
        IdmConfigParser(file_name=self.tempfile_ini.name)

        sys.stdout = mock_stdout
        logger_demo.write_some_logs(user=True, root=True, comps=True, exp=True, full=False, check=True)

        with open(f"{self.case_name}.log", "r") as log_file_fd:
            log_file_content = log_file_fd.read()
            # validate root should be WARNING and above. user should be WARNING and above
            matched = re.search(r"write_some_logs \[WARNING\] - root: 3", log_file_content)
            self.assertTrue(matched)
            matched = re.search(r"write_some_logs \[ERROR\] - root: 4", log_file_content)
            self.assertTrue(matched)
            matched = re.search(r"write_some_logs \[CRITICAL\] - root: 5", log_file_content)
            self.assertTrue(matched)
            matched = re.search(r"write_some_logs \[DEBUG\] - root: 1", log_file_content)
            self.assertFalse(bool(matched))  # no DEBUG for root
            matched = re.search(r"write_some_logs \[INFO\] - root: 2", log_file_content)
            self.assertFalse(bool(matched))  # no INFO for root

            matched = re.search(r"write_some_logs \[DEBUG\] - user: 11", log_file_content)
            self.assertFalse(bool(matched))  # no DEBUG for user
            matched = re.search(r"write_some_logs \[INFO\] - user: 22", log_file_content)
            self.assertFalse(bool(matched))  # no INFO for user
            matched = re.search(r"write_some_logs \[WARNING\] - user: 33", log_file_content)
            self.assertTrue(matched)
            matched = re.search(r"write_some_logs \[ERROR\] - user: 44", log_file_content)
            self.assertTrue(matched)
            matched = re.search(r"write_some_logs \[CRITICAL\] - user: 55", log_file_content)
            self.assertTrue(matched)
            log_file_fd.close()

        stdout = mock_stdout.getvalue()
        self.validate_color_console(stdout)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_console_on_log_off(self, mock_stdout):
        ini_content = f"""
        [Logging]
            console = on
            enable_file_logging = off
            filename ={self.case_name}.log
        """
        self.create_temp_ini(ini_content)
        IdmConfigParser(file_name=self.tempfile_ini.name)

        sys.stdout = mock_stdout
        logger_demo.write_some_logs(user=True, root=True, comps=True, exp=True, full=False, check=False)
        # validate no log file generate
        self.assertFalse(os.path.exists(f"{self.case_name}.log"))

        stdout = mock_stdout.getvalue()
        self.validate_default_user_console_on(stdout)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_console_off_log_off(self, mock_stdout):
        ini_content = f"""
        [Logging]
            console = off
            enable_file_logging = off
            filename ={self.case_name}.log
        """
        self.create_temp_ini(ini_content)
        IdmConfigParser(file_name=self.tempfile_ini.name)

        sys.stdout = mock_stdout
        logger_demo.write_some_logs(user=True, root=True, comps=True, exp=True, full=False, check=False)
        # validate no log file generate
        self.assertFalse(os.path.exists(f"{self.case_name}.log"))

        stdout = mock_stdout.getvalue()
        self.validate_default_user_console_off(stdout)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_console_on_user_output_on(self, mock_stdout):
        ini_content = f"""
        [Logging]
            level = CRITICAL
            console = on
            enable_file_logging = off
            user_output = on
        """
        self.create_temp_ini(ini_content)
        IdmConfigParser(file_name=self.tempfile_ini.name)

        sys.stdout = mock_stdout
        logger_demo.write_some_logs(user=True, root=True, comps=True, exp=True, full=False, check=False)
        self.assertFalse(os.path.exists(f"{self.case_name}.log"))

        stdout = mock_stdout.getvalue()
        matched = re.search(r"CRITICAL.*root: 5", stdout)
        self.assertTrue(matched)
        matched = re.search(r"CRITICAL.*user: 55", stdout)
        self.assertTrue(matched)

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
        self.create_temp_ini(ini_content)
        IdmConfigParser(file_name=self.tempfile_ini.name)

        sys.stdout = mock_stdout
        logger_demo.write_some_logs(user=True, root=True, full=False, check=False)
        self.assertFalse(os.path.exists(f"{self.case_name}.log"))

        stdout = mock_stdout.getvalue()
        self.validate_color_console(stdout)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_use_colored_logs_off(self, mock_stdout):
        ini_content = f"""
        [Logging]
            console = off
            enable_file_logging = off
            user_output = on
            use_colored_logs = off
        """
        self.create_temp_ini(ini_content)
        IdmConfigParser(file_name=self.tempfile_ini.name)
        sys.stdout = mock_stdout
        logger_demo.write_some_logs(user=True, root=True, check=False)
        self.assertFalse(os.path.exists(f"{self.case_name}.log"))

        stdout = mock_stdout.getvalue()
        self.validate_default_user_console_off(stdout)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_enable_file_logging(self, mock_stdout):
        ini_content = f"""
        [Logging]
            enable_file_logging = off
        """
        self.create_temp_ini(ini_content)
        IdmConfigParser(file_name=self.tempfile_ini.name)
        sys.stdout = mock_stdout
        logger_demo.write_some_logs(user=True, root=True, comps=True, exp=True, full=False, check=False)
        self.assertFalse(os.path.exists(f"{self.case_name}.log"))

        stdout = mock_stdout.getvalue()
        self.validate_default_user_console_on(stdout)

    def validate_default_user_console_off(self, stdout):
        matched = re.search(r"user: 11", stdout)
        self.assertFalse(bool(matched))  # should not print debug user, since user is VERBOSE now
        matched = re.search(r"user: 22", stdout)
        self.assertTrue(matched)
        matched = re.search(r"user: 33", stdout)
        self.assertTrue(matched)
        matched = re.search(r"user: 44", stdout)
        self.assertTrue(matched)
        matched = re.search(r"user: 55", stdout)
        self.assertTrue(matched)

    def validate_color_console(self, stdout):
        matched = re.search(r"user: 11", stdout)
        self.assertFalse(bool(matched))  # should not print debug user, since user is VERBOSE now
        matched = re.search(r"user: 22", stdout)
        self.assertTrue(matched)
        matched = re.search(r"33muser: 33", stdout)
        self.assertTrue(matched)
        matched = re.search(r"31muser: 44", stdout)
        self.assertTrue(matched)
        matched = re.search(r"1;31muser: 55", stdout)
        self.assertTrue(matched)

    def validate_default_user_console_on(self, stdout):
        matched = re.search(r"WARNING.*root: 3", stdout)
        self.assertTrue(matched)
        matched = re.search(r"ERROR.*root: 4", stdout)
        self.assertTrue(matched)
        matched = re.search(r"CRITICAL.*root: 5", stdout)
        self.assertTrue(matched)
        matched = re.search(r"WARNING.*user: 33", stdout)
        self.assertTrue(matched)
        matched = re.search(r"ERROR.*user: 44", stdout)
        self.assertTrue(matched)
        matched = re.search(r"CRITICAL.*user: 55", stdout)
        self.assertTrue(matched)

    def create_temp_ini(self, ini_str):
        self.tempfile_ini = tempfile.NamedTemporaryFile(mode='wb', delete=False)
        self.tempfile_ini.write(ini_str.replace("\r", "").encode('utf-8'))
        self.tempfile_ini.flush()
