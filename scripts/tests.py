# -*- coding: utf-8 -*-
# Copyright 2015 Elico Corp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import unittest
from addons import *


class RepoTest(unittest.TestCase):

    def test_check_is_url(self):
        dependent = 'connector'
        self.repo = Repo(dependent)
        self.assertTrue(self.repo._check_is_url('https://github.com'))
        self.assertTrue(self.repo._check_is_url('http://github.com'))
        self.assertFalse(self.repo._check_is_url('ttps://github.com'))

    def test_parse_oca_repo(self):
        dependent = 'connector'
        self.repo = Repo(dependent)
        self.repo._parse_organization_repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.organization, DEFAULT_ORGANIZATION)
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.folder_name, 'connector')

    def test_parse_organization_and_repo(self):
        dependent = 'OCA/connector'
        self.repo = Repo(dependent)
        self.repo._parse_organization_repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.organization, DEFAULT_ORGANIZATION)
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.folder_name, 'connector')

    def test_parse_url(self):
        dependent = 'https://github.com/OCA/connector'
        self.repo = Repo(dependent)
        self.repo._parse_url(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.organization, DEFAULT_ORGANIZATION)
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.folder_name, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')

    def test_path(self):
        dependent = 'connector'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.path, '%sconnector' % (EXTRA_ADDONS_PATH, ))

    def test_repo_oca_repo(self):
        dependent = 'connector'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.folder_name, 'connector')
        self.assertEquals(self.repo.branch, None)
        self.assertEquals(self.repo.organization, DEFAULT_ORGANIZATION)
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '%sconnector' % (EXTRA_ADDONS_PATH, ))

    def test_repo_organization_and_repo(self):
        dependent = 'OCA/connector'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.folder_name, 'connector')
        self.assertEquals(self.repo.branch, None)
        self.assertEquals(self.repo.organization, DEFAULT_ORGANIZATION)
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '%sconnector' % (EXTRA_ADDONS_PATH, ))

    def test_repo_url(self):
        dependent = 'https://github.com/OCA/connector'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.folder_name, 'connector')
        self.assertEquals(self.repo.branch, None)
        self.assertEquals(self.repo.organization, DEFAULT_ORGANIZATION)
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '%sconnector' % (EXTRA_ADDONS_PATH, ))

    def test_repo_oca_repo_and_branch(self):
        dependent = 'connector 8.0'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.folder_name, 'connector')
        self.assertEquals(self.repo.branch, '8.0')
        self.assertEquals(self.repo.organization, DEFAULT_ORGANIZATION)
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '%sconnector' % (EXTRA_ADDONS_PATH, ))

    def test_repo_organization_and_repo_and_branch(self):
        dependent = 'OCA/connector 8.0'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.folder_name, 'connector')
        self.assertEquals(self.repo.branch, '8.0')
        self.assertEquals(self.repo.organization, DEFAULT_ORGANIZATION)
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '%sconnector' % (EXTRA_ADDONS_PATH, ))

    def test_repo_url_and_branch(self):
        dependent = 'https://github.com/OCA/connector 8.0'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.folder_name, 'connector')
        self.assertEquals(self.repo.branch, '8.0')
        self.assertEquals(self.repo.organization, DEFAULT_ORGANIZATION)
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '%sconnector' % (EXTRA_ADDONS_PATH, ))

    def test_repo_rename_and_url(self):
        dependent = 'connector_rename https://github.com/OCA/connector'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.folder_name, 'connector_rename')
        self.assertEquals(self.repo.branch, None)
        self.assertEquals(self.repo.organization, DEFAULT_ORGANIZATION)
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '%sconnector_rename' % (EXTRA_ADDONS_PATH, ))

    def test_repo_rename_and_url_and_branch(self):
        dependent = 'connector_rename https://github.com/OCA/connector 8.0'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.folder_name, 'connector_rename')
        self.assertEquals(self.repo.branch, '8.0')
        self.assertEquals(self.repo.organization, DEFAULT_ORGANIZATION)
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '%sconnector_rename' % (EXTRA_ADDONS_PATH, ))

    def test_repo_rename_and_url_and_branch_new(self):
        dependent = 'account-financial-reporting https://github.com/OCA/account-financial-reporting 8.0'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.folder_name, 'account-financial-reporting')
        self.assertEquals(self.repo.branch, '8.0')
        self.assertEquals(self.repo.organization, DEFAULT_ORGANIZATION)
        self.assertEquals(self.repo.repository, 'account-financial-reporting')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '%saccount-financial-reporting' % (EXTRA_ADDONS_PATH, ))

    def test_download_cmd(self):
        repo = Repo('Elico-Corp/odoo')
        self.assertEqual(
            ['git', 'clone',
             'https://github.com/Elico-Corp/odoo.git',
             '/mnt/data/additional_addons/odoo'],
            repo.download_cmd)

    def test_download_cmd_with_branch(self):
        repo = Repo('Elico-Corp/odoo 8.0')
        self.assertEqual(
            ['git', 'clone', '-b', '8.0',
             'https://github.com/Elico-Corp/odoo.git',
             '/mnt/data/additional_addons/odoo'],
            repo.download_cmd)

if __name__ == '__main__':
    unittest.main()
