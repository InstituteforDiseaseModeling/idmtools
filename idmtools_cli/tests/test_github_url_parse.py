import allure
import os
import unittest
from unittest import TestCase

import pytest
# from idmtools_cli.utils.gitrepo import GitRepo
from idmtools.utils.gitrepo import GitRepo


@pytest.mark.smoke
@allure.story("CLI")
@allure.story("Examples Command")
@allure.suite("idmtools_core")
class TestGithubUrlParse(TestCase):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def test_default_owner_and_repo(self):
        gr = GitRepo()
        self.assertEqual(gr.repo_owner, 'institutefordiseasemodeling')
        self.assertEqual(gr.repo_name, 'idmtools')
        self.assertEqual(gr.branch, 'main')

    def test_owner_and_repo(self):
        gr = GitRepo(repo_owner='test_owner', repo_name='test_repo')
        self.assertEqual(gr.repo_owner, 'test_owner')
        self.assertEqual(gr.repo_name, 'test_repo')
        self.assertEqual(gr.branch, 'main')
        self.assertEqual(gr.path, '')

    def test_owner_and_repo_with_url_parse(self):
        url = "https://github.com/InstituteforDiseaseModeling/idmtools/tree/dev/examples/ssmt"

        gr = GitRepo(repo_owner='test_owner', repo_name='test_repo')
        gr.parse_url(url)
        self.assertEqual(gr.repo_owner, 'institutefordiseasemodeling')
        self.assertEqual(gr.repo_name, 'idmtools')
        self.assertEqual(gr.branch, 'dev')
        self.assertEqual(gr.path, 'examples/ssmt')

    def test_full_url(self):
        url = "https://github.com/InstituteforDiseaseModeling/idmtools/tree/dev/examples/ssmt"

        gr = GitRepo()
        gr.parse_url(url)
        self.assertEqual(gr.repo_owner, 'institutefordiseasemodeling')
        self.assertEqual(gr.repo_name, 'idmtools')
        self.assertEqual(gr.branch, 'dev')
        self.assertEqual(gr.path, 'examples/ssmt')

    def test_short_url(self):
        url = "https://github.com/InstituteforDiseaseModeling/corvid-idmtools"

        gr = GitRepo()
        gr.parse_url(url)
        self.assertEqual(gr.repo_owner, 'institutefordiseasemodeling')
        self.assertEqual(gr.repo_name, 'corvid-idmtools')
        self.assertEqual(gr.branch, 'main')
        self.assertEqual(gr.path, '')

    def test_full_url_with_branch(self):
        url = "https://github.com/InstituteforDiseaseModeling/idmtools/tree/dev/examples/ssmt"

        gr = GitRepo()
        gr.parse_url(url, branch='main')
        self.assertEqual(gr.repo_owner, 'institutefordiseasemodeling')
        self.assertEqual(gr.repo_name, 'idmtools')
        self.assertEqual(gr.branch, 'main')
        self.assertEqual(gr.path, 'examples/ssmt')

    def test_short_url_with_branch(self):
        url = "https://github.com/InstituteforDiseaseModeling/corvid-idmtools"

        gr = GitRepo()
        gr.parse_url(url, branch='dev')
        self.assertEqual(gr.repo_owner, 'institutefordiseasemodeling')
        self.assertEqual(gr.repo_name, 'corvid-idmtools')
        self.assertEqual(gr.branch, 'dev')
        self.assertEqual(gr.path, '')

    def test_file_url(self):
        url = "https://github.com/InstituteforDiseaseModeling/idmtools/blob/dev/examples/ssmt/__init__.py"

        gr = GitRepo()
        gr.parse_url(url)
        self.assertEqual(gr.repo_owner, 'institutefordiseasemodeling')
        self.assertEqual(gr.repo_name, 'idmtools')
        self.assertEqual(gr.branch, 'dev')
        self.assertEqual(gr.path, 'examples/ssmt/__init__.py')

    def test_general_url(self):
        url = "https://github.com/test_owner/test_repo/tree/main/test_example_path"

        gr = GitRepo()
        gr.parse_url(url)
        self.assertEqual(gr.repo_owner, 'test_owner')
        self.assertEqual(gr.repo_name, 'test_repo')
        self.assertEqual(gr.branch, 'main')
        self.assertEqual(gr.path, 'test_example_path')


if __name__ == '__main__':
    unittest.main()
