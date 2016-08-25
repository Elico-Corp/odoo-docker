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
import re
from urlparse import urlparse
from subprocess import call
from subprocess import check_output

DOWNLOAD_PATH = '/mnt/data/additional_addons/'
ODOO_CONF = '/opt/odoo/etc/odoo.conf'
ADDONS_PATH = ['/opt/odoo/sources/odoo/addons']
SCHEME = 'https://'
GIT_REPOSITORY_HOSTING_SERVICE = 'github.com'
DEFAULT_ORGANIZATION = 'OCA'


class Repo(object):
    """
    oca_dependencies.txt

    For public repo:

    oca-repo -> https://github.com/OCA/oca-repo (branch: master)
    oca-repo 8.0 -> https://github.com/OCA/oca-repo (branch: 8.0)
    organization/public-repo -> https://github.com/organization/public-repo (branch: master)
    organization/public-repo 8.0 -> https://github.com/organization/public-repo (branch: 8.0)
    https://github.com/organization/public-repo -> https://github.com/organization/public-repo (branch: master)
    https://github.com/organization/public-repo 8.0 -> https://github.com/organization/public-repo (branch: 8.0)
    public-repo_rename https://github.com/organization/public-repo -> https://github.com/organization/public-repo (branch: master)
    public-repo_rename https://github.com/organization/public-repo 8.0 -> https://github.com/organization/public-repo (branch: 8.0)

    For private repo:

    git@github.com:Elico-Corp/private_repo
    git@github.com:Elico-Corp/private_repo 8.0
    private_repo_rename git@github.com:Elico-Corp/private-repo
    private_repo_rename git@github.com:Elico-Corp/private_repo 8.0

    """
    def __init__(self, dependent):
        self.dependent = dependent
        self.short_dependent = None
        self.branch = None
        self.organization = DEFAULT_ORGANIZATION
        self.repository = None
        self.scheme = SCHEME
        self.git_repo_host = GIT_REPOSITORY_HOSTING_SERVICE
        self._parse()

    def _check_is_ssh(self, url):
        if url.startswith('git@github.com:'):
            self.scheme = 'git@'
            self.git_repo_host = 'github.com:'
            return True

    def _check_is_url(self, url):
        if re.match(r'^https?:/{2}\w.+$', url):
            return True
        else:
            if self._check_is_ssh(url):
                return True
            return False

    def _parse_organization_repo(self, dependent):
        _args = dependent.split('/')
        _len_args = len(_args)
        if _len_args == 1:
            self.repository = _args[0]
            self.short_dependent = self.repository
        elif _len_args == 2:
            self.organization = _args[0]
            self.repository = _args[1]
            self.short_dependent = self.repository

    def _parse_url(self, url):
        if self.scheme == SCHEME:
            _url_parse = urlparse(url)
            self.git_repo_host = _url_parse.netloc
            _args_path = _url_parse.path.split('/')
            self.organization = _args_path[1]
            self.repository = _args_path[2].replace('.git', '')
            self.short_dependent = self.repository
        elif self.scheme == 'git@':
            _args = url.split(':')[1]
            _args_path = _args.split('/')
            self.organization = _args_path[0]
            self.repository = _args_path[1].replace('.git', '')
            self.short_dependent = self.repository

    def _parse(self):
        _dependent = self.dependent
        _args = _dependent.split(' ')
        _len_args = len(_args)
        if _len_args == 1:
            if self._check_is_url(_args[0]):
                # url
                self._parse_url(_args[0])
            else:
                # repo OR organization/repo
                self._parse_organization_repo(_args[0])
        elif _len_args == 2:
            if self._check_is_url(_args[0]):
                # url AND branch
                self._parse_url(_args[0])
                self.branch = _args[1]
            else:
                if self._check_is_url(_args[1]):
                    # repo AND url
                    self._parse_url(_args[1])
                    self.short_dependent = _args[0]
                else:
                    # repo OR organization/repo AND branch
                    self._parse_organization_repo(_args[0])
                    self.branch = _args[1]
        elif _len_args == 3:
            if self._check_is_url(_args[1]):
                # repo OR organization/repo AND url AND branch
                self._parse_organization_repo(_args[0])
                self._parse_url(_args[1])
                self.branch = _args[2]
                self.short_dependent = _args[0]

    @property
    def path(self):
        return '%s%s' % (DOWNLOAD_PATH, self.short_dependent)

    @property
    def resolve_url(self):
        _resolve_url = '%s%s/%s/%s.git' % (
            self.scheme,
            self.git_repo_host,
            self.organization,
            self.repository
        )
        return _resolve_url

    @property
    def download_cmd(self):
        if self.branch:
            cmd = 'git clone -b %s %s %s' % (
                self.branch, self.resolve_url, self.path
            )
        else:
            cmd = 'git clone %s %s' % (
                self.resolve_url, self.path
            )
        return cmd.split()

    @property
    def update_cmd(self):
        if self.branch:
            cmd = 'git --git-dir=%s/.git --work-tree=%s pull origin %s' % (
                self.path, self.path, self.branch
            )
            return cmd.split()
        else:
            branch_cmd = 'git --git-dir=%s/.git --work-tree=%s branch' % (
                self.path, self.path
            )
            output = check_output(branch_cmd, shell=True)
            for line in output.split('\n'):
                if line.startswith('*'):
                    self.branch = line.replace('* ', '')
                    cmd = 'git --git-dir=%s/.git --work-tree=%s pull origin %s' % (
                        self.path, self.path, self.branch
                    )
                    return cmd.split()

    def download(self):
        if self.path in ADDONS_PATH:
            return
        if os.path.exists(self.path):
            print('PULL: %s' % (self.path,))
            cmd = self.update_cmd
            call(cmd)
        else:
            print('CLONE: %s' % (self.path, ))
            call(self.download_cmd)
        ADDONS_PATH.append(self.path)
        self.download_dependency()

    def download_dependency(self):
        filename = '%s/oca_dependencies.txt' % self.path
        if not os.path.exists(filename):
            return
        repo_list = []
        with open(filename) as f:
            for line in f:
                l = line.strip('\n').strip()
                if l.startswith('#') or not l:
                    continue
                repo_list.append(Repo(l))
        f.close()
        for repo in repo_list:
            repo.download()


def write_addons_path():
    with open(ODOO_CONF, 'a') as f:
        f.write('addons_path = %s' % ','.join(list(set(ADDONS_PATH))))
    f.close()


def main():
    dependent = os.environ.get('ADDONS_REPO')
    if dependent:
        print('dependent: %s ' % (dependent, ))
        Repo(dependent).download()
    write_addons_path()

if __name__ == '__main__':
    main()
