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
import os
from subprocess import call

DOWNLOAD_PATH = '/mnt/data/additional_addons/'
ODOO_CONF = '/opt/odoo/etc/odoo.conf'
addons_path = ['/opt/odoo/sources/odoo/addons']


class Repo(object):
    def __init__(self, name):
        self.name = name

    @property
    def short_name(self):
        return self.name.partition('/')[-1].partition(':')[0]

    @property
    def tag(self):
        _tag = self.name.partition(':')[-1]
        if _tag:
            return _tag
        return 'master'

    @property
    def project(self):
        return self.name.partition(':')[0]

    @property
    def organization(self):
        return self.project.split('/')[0]

    @property
    def download_cmd(self):
        cmd = 'git clone -b %s --depth 1 git@github.com:%s.git %s' % (
            self.tag, self.project, self.path)
        return cmd.split()

    @property
    def update_cmd(self):
        cmd = 'cd %s && git pull origin %s && cd -' % (self.path, self.tag)
        return cmd.split()

    @property
    def path(self):
        return '%s%s' % (DOWNLOAD_PATH, self.short_name)

    def download(self):
        # if just download
        if self.path in addons_path:
            return
        if os.path.exists(self.path):
            call(self.update_cmd)
        else:
            call(self.download_cmd)
        addons_path.append(self.path)
        self.download_dependency()

    def download_dependency(self):
        filename = '%s/oca_dependencies.txt' % self.path
        if not os.path.exists(filename):
            return
        links = []
        with open(filename) as f:
            for line in f:
                l = line.strip('\n').strip()
                if l.startswith('#') or not l:
                    continue
                links.append(self.clean_dependency_link(l))
        f.close()
        for link in links:
            Repo(link).download()

    def clean_dependency_link(self, link):
        if len(link.split()) == 1:
            # if it's an organization repo
            return '%s/%s:%s' % (self.organization, link, self.tag)
        return link.split('github.com/')[-1].replace(' ', ':')


def write_addons_path():
    with open(ODOO_CONF, 'a') as f:
        f.write('addons_path = %s' % ','.join(list(set(addons_path))))
    f.close()


def main():
    name = os.environ.get('GITHUB_REPO')
    if name:
        print name
        Repo(name).download()
    write_addons_path()

if __name__ == '__main__':
    main()
