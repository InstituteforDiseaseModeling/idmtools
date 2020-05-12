import os
import unittest
from click.testing import CliRunner
from idmtools_cli.cli.example import example, get_plugins_examples, validate
from idmtools_test.utils.cli import get_subcommands_from_help_result, run_command


class TestExample(unittest.TestCase):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(example, ['--help'])
        # Check for our help string
        self.assertIn('Download examples from GitHub repo to user location', result.output)
        # Ensure we have our expected global sub-commands
        commands = get_subcommands_from_help_result(result)
        self.assertIn('download', commands)

    def test_example_help(self):
        result = run_command('example', '--help')
        # Check for our help string
        self.assertIn('Download examples from GitHub repo to user location', result.output)
        # Ensure we have our expected global sub-commands
        commands = get_subcommands_from_help_result(result)
        self.assertIn('download', commands)

    def test_download_help(self):
        runner = CliRunner()
        result = runner.invoke(example, ['download', '--help'])
        self.assertIn('Download examples from GitHub repo to user location', result.output)
        # Check that there is a --url option
        self.assertIn('--url', result.output)
        # Check that there is a --output option
        self.assertIn('--output', result.output)
        # print(result.output)

    def test_get_plugins_example_urls(self):
        examples = get_plugins_examples()
        self.assertTrue(isinstance(examples, dict))
        self.assertTrue('COMPSPlatform' in examples)

    def test_public_repos(self):
        result = run_command('example', 'repos')
        # Check for special public repo
        self.assertIn('https://github.com/InstituteforDiseaseModeling/EMOD', result.output)

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

