import allure
import os
import unittest
import pytest
from click.testing import CliRunner
os.environ['IDMTOOLS_LOGGING_USE_COLORED_LOGS'] = 'f'
os.environ['IDMTOOLS_HIDE_DEV_WARNING'] = '1'
from idmtools_cli.cli.gitrepo import gitrepo, get_plugins_examples, validate
from idmtools_test.utils.cli import get_subcommands_from_help_result, run_command


@pytest.mark.smoke
@allure.story("CLI")
@allure.story("Examples Command")
@allure.suite("idmtools_cli")
class TestExample(unittest.TestCase):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(gitrepo, ['--help'])
        # Check for our help string
        self.assertIn('Download files from GitHub repo to user location', result.output)
        # Ensure we have our expected global sub-commands
        commands = get_subcommands_from_help_result(result)
        self.assertIn('download', commands)

    def test_example_help(self):
        result = run_command('gitrepo', '--help')
        # Check for our help string
        self.assertIn('Download files from GitHub repo to user location', result.output)
        # Ensure we have our expected global sub-commands
        commands = get_subcommands_from_help_result(result)
        self.assertIn('download', commands)

    def test_download_help(self):
        runner = CliRunner()
        result = runner.invoke(gitrepo, ['download', '--help'])
        self.assertIn('Download files from GitHub repo to user location', result.output)
        # Check that there is a --url option
        self.assertIn('--url', result.output)
        # Check that there is a --output option
        self.assertIn('--output', result.output)

    def test_get_plugins_example_urls(self):
        examples = get_plugins_examples()
        self.assertTrue(isinstance(examples, dict))
        self.assertTrue('COMPSPlatform' in examples)

    def test_public_repos(self):
        # because of weirdness in testing, the log output even when set to stdout appears as stderr. We workaround by capturing both independently
        result = run_command('gitrepo', 'repos', mix_stderr=False)
        # Check for special public repo
        self.assertIn('https://github.com/InstituteforDiseaseModeling/EMOD', result.stdout)

    def test_validate(self):
        choice_set = {1, 2, 3, 4, 5, 6, 7, 8, 'all'}
        r1, _ = validate("1 2 3", choice_set)
        self.assertTrue(r1)
        self.assertSetEqual(set(_), set([1, 2, 3]))

        r2, _ = validate("1 2 3 all", choice_set)
        self.assertTrue(r2)
        self.assertEqual(_, ['all'])

        r3, _ = validate("1  3  , 9", choice_set)
        self.assertFalse(r3)
        self.assertSetEqual(set(_), set([9, ',']))

        r4, _ = validate("1  3 9   10", choice_set)
        self.assertFalse(r4)
        self.assertSetEqual(set(_), set([9, 10]))

        r5, _ = validate("1  3 all 9", choice_set)
        self.assertFalse(r5)
        self.assertEqual(_, [9])

