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

    def test_short_name(self):
        repo = Repo('Elico-Corp/odoo:8.0')
        self.assertEqual('odoo', repo.short_name)

    def test_get_project(self):
        repo = Repo('Elico-Corp/odoo:8.0')
        self.assertEqual('Elico-Corp/odoo', repo.project)

    def test_get_organization(self):
        repo = Repo('Elico-Corp/odoo:8.0')
        self.assertEqual('Elico-Corp', repo.organization)

    def test_get_tag(self):
        repo = Repo('Elico-Corp/odoo:8.0')
        self.assertEqual('8.0', repo.tag)

    def test_get_tag_when_no_tag(self):
        repo = Repo('Elico-Corp/odoo')
        self.assertEqual('master', repo.tag)

    def test_download_cmd(self):
        repo = Repo('Elico-Corp/odoo')
        self.assertEqual(
            ['git', 'clone', '-b', 'master', '--depth', '1',
             'git@github.com:Elico-Corp/odoo.git',
             '/mnt/data/additional_addons/odoo'],
            repo.download_cmd)

    def test_update_cmd(self):
        repo = Repo('Elico-Corp/odoo:8.0')
        self.assertEqual(
            ['cd', '/mnt/data/additional_addons/odoo', '&&', 'git', 'pull',
             'origin', '8.0', '&&', 'cd', '-'],
            repo.update_cmd)

    def test_path(self):
        repo = Repo('Elico-Corp/odoo:8.0')
        self.assertEqual('/mnt/data/additional_addons/odoo', repo.path)

    def test_dependency_link(self):
        repo = Repo('Elico-Corp/odoo:8.0')
        link = 'account-financial-reporting\
 https://github.com/OCA/account-financial-reporting 8.0'
        self.assertEqual(
            'OCA/account-financial-reporting:8.0',
            repo.clean_dependency_link(link))

    def test_dependency_link_organization(self):
        repo = Repo('Elico-Corp/odoo:8.0')
        link = 'connector'
        self.assertEqual(
            'Elico-Corp/connector:8.0',
            repo.clean_dependency_link(link))

if __name__ == '__main__':
    unittest.main()
