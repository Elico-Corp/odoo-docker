# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (c) 2010-2015 Elico Corp.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import unittest
from addons import Repo


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
        self.assertEquals(self.repo.organization, 'OCA')
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.short_dependent, 'connector')

    def test_parse_organization_and_repo(self):
        dependent = 'OCA/connector'
        self.repo = Repo(dependent)
        self.repo._parse_organization_repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.organization, 'OCA')
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.short_dependent, 'connector')

    def test_parse_url(self):
        dependent = 'https://github.com/OCA/connector'
        self.repo = Repo(dependent)
        self.repo._parse_url(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.organization, 'OCA')
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.short_dependent, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')

    def test_path(self):
        dependent = 'connector'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.path, '/mnt/data/additional_addons/connector')

    def test_repo_oca_repo(self):
        dependent = 'connector'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.short_dependent, 'connector')
        self.assertEquals(self.repo.branch, None)
        self.assertEquals(self.repo.organization, 'OCA')
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '/mnt/data/additional_addons/connector')

    def test_repo_organization_and_repo(self):
        dependent = 'OCA/connector'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.short_dependent, 'connector')
        self.assertEquals(self.repo.branch, None)
        self.assertEquals(self.repo.organization, 'OCA')
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '/mnt/data/additional_addons/connector')

    def test_repo_url(self):
        dependent = 'https://github.com/OCA/connector'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.short_dependent, 'connector')
        self.assertEquals(self.repo.branch, None)
        self.assertEquals(self.repo.organization, 'OCA')
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '/mnt/data/additional_addons/connector')

    def test_repo_oca_repo_and_branch(self):
        dependent = 'connector 8.0'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.short_dependent, 'connector')
        self.assertEquals(self.repo.branch, '8.0')
        self.assertEquals(self.repo.organization, 'OCA')
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '/mnt/data/additional_addons/connector')

    def test_repo_organization_and_repo_and_branch(self):
        dependent = 'OCA/connector 8.0'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.short_dependent, 'connector')
        self.assertEquals(self.repo.branch, '8.0')
        self.assertEquals(self.repo.organization, 'OCA')
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '/mnt/data/additional_addons/connector')

    def test_repo_url_and_branch(self):
        dependent = 'https://github.com/OCA/connector 8.0'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.short_dependent, 'connector')
        self.assertEquals(self.repo.branch, '8.0')
        self.assertEquals(self.repo.organization, 'OCA')
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '/mnt/data/additional_addons/connector')

    def test_repo_rename_and_url(self):
        dependent = 'connector_rename https://github.com/OCA/connector'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.short_dependent, 'connector_rename')
        self.assertEquals(self.repo.branch, None)
        self.assertEquals(self.repo.organization, 'OCA')
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '/mnt/data/additional_addons/connector_rename')

    def test_repo_rename_and_url_and_branch(self):
        dependent = 'connector_rename https://github.com/OCA/connector 8.0'
        self.repo = Repo(dependent)
        self.assertEquals(self.repo.dependent, dependent)
        self.assertEquals(self.repo.short_dependent, 'connector_rename')
        self.assertEquals(self.repo.branch, '8.0')
        self.assertEquals(self.repo.organization, 'OCA')
        self.assertEquals(self.repo.repository, 'connector')
        self.assertEquals(self.repo.git_repo_host, 'github.com')
        self.assertEquals(self.repo.path, '/mnt/data/additional_addons/connector_rename')

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
