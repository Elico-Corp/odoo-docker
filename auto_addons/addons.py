# -*- coding: utf-8 -*-
# Copyright 2015 Elico Corp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import os
import re
import sys
from os import remove
from shutil import move
from urlparse import urlparse
from subprocess import call
from subprocess import check_output

EXTRA_ADDONS_PATH = '/opt/odoo/additional_addons/'
OLD_ODOO_CONF = '/opt/odoo/etc/odoo.conf.old'
ODOO_CONF = '/opt/odoo/etc/odoo.conf'
ADDONS_PATH = ['/opt/odoo/sources/odoo/addons']
DEFAULT_SCHEME = 'https://'
DEFAULT_GIT_REPO_HOSTING_SERVICE = 'github.com'
DEFAULT_ORGANIZATION = 'OCA'
DEPENDENCIES_FILE = 'oca_dependencies.txt'
REGEX_ADDONS_PATH = r'^addons_path\s*=\s*'


class Repo(object):
    """
    oca_dependencies.txt

    For public repo:

    oca-repo -> https://github.com/OCA/oca-repo (default branch)
    oca-repo 8.0 -> https://github.com/OCA/oca-repo (branch: 8.0)
    organization/public-repo -> https://github.com/organization/public-repo (default branch)
    organization/public-repo 8.0 -> https://github.com/organization/public-repo (branch: 8.0)
    https://github.com/organization/public-repo -> https://github.com/organization/public-repo (default branch)
    https://github.com/organization/public-repo 8.0 -> https://github.com/organization/public-repo (branch: 8.0)
    public_repo_rename https://github.com/organization/public-repo -> https://github.com/organization/public-repo (default branch)
    public_repo_rename https://github.com/organization/public-repo 8.0 -> https://github.com/organization/public-repo (branch: 8.0)

    For private repo:

    git@github.com:Elico-Corp/private-repo
    git@github.com:Elico-Corp/private-repo 8.0
    private_repo_rename git@github.com:Elico-Corp/private-repo
    private_repo_rename git@github.com:Elico-Corp/private-repo 8.0

    """
    def __init__(self, remote_url, parent=None):
        if parent:
            self.parent = parent
            self.branch = self.parent.branch
        else:
            self.parent = None
            self.branch = None
        self.remote_url = remote_url
        self.folder_name = None
        self.organization = DEFAULT_ORGANIZATION
        self.repository = None
        self.scheme = DEFAULT_SCHEME
        self.git_repo_host = DEFAULT_GIT_REPO_HOSTING_SERVICE
        self._parse()

    def _set_branch(self, branch):
        self.branch = branch if branch else self.parent.branch

    def _check_is_ssh(self, url):
        # TODO For other hosting services, this part should be dynamic.
        # TODO support URL like ssh://git@gitlab.domain.name:10022
        # TODO Maybe we could consider using a standard URL parser in the future.
        if url.startswith('git@github.com:'):
            self.scheme = 'git@'
            self.git_repo_host = 'github.com:'
            return True

    def _check_is_url(self, url):
        return re.match(r'^https?:/{2}\w.+$', url) \
            or self._check_is_ssh(url)

    def fetch_branch_name(self):
        branch_cmd = 'git --git-dir=%s/.git --work-tree=%s branch' % (
            self.path, self.path
        )
        output = check_output(branch_cmd, shell=True)
        for line in output.split('\n'):
            if line.startswith('*'):
                self._set_branch(line.replace('* ', ''))

    def _parse_organization_repo(self, remote_url):
        _args = remote_url.split('/')
        _len_args = len(_args)
        if _len_args == 1:
            # repo
            self.repository = _args[0]
            self.folder_name = self.repository
        elif _len_args == 2:
            # organization AND repo
            self.organization = _args[0]
            self.repository = _args[1]
            self.folder_name = self.repository

    def _parse_url(self, url):
        if self.scheme == DEFAULT_SCHEME:
            _url_parse = urlparse(url)
            self.git_repo_host = _url_parse.netloc
            _args_path = _url_parse.path.split('/')
            self.organization = _args_path[1]
            self.repository = _args_path[2].replace('.git', '')
            self.folder_name = self.repository
        elif self.scheme == 'git@':
            _args = url.split(':')[1]
            _args_path = _args.split('/')
            self.organization = _args_path[0]
            self.repository = _args_path[1].replace('.git', '')
            self.folder_name = self.repository

    def _parse(self):
        _remote_url = self.remote_url
        _args = _remote_url.split(' ')
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
                self._set_branch(_args[1])
            else:
                if self._check_is_url(_args[1]):
                    # repo AND url
                    self._parse_url(_args[1])
                    self.folder_name = _args[0]
                else:
                    # repo OR organization/repo AND branch
                    self._parse_organization_repo(_args[0])
                    self._set_branch(_args[1])
        elif _len_args == 3:
            if self._check_is_url(_args[1]):
                # repo OR organization/repo AND url AND branch
                self._parse_organization_repo(_args[0])
                self._parse_url(_args[1])
                self._set_branch(_args[2])
                self.folder_name = _args[0]

    @property
    def path(self):
        return '%s%s' % (EXTRA_ADDONS_PATH, self.folder_name)

    @property
    def resolve_url(self):
        _resolve_url_str = '%s%s/%s/%s.git'
        if self.scheme == 'git@':
            _resolve_url_str = '%s%s%s/%s.git'

        _resolve_url = _resolve_url_str % (
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
            self.fetch_branch_name()
            cmd = 'git --git-dir=%s/.git --work-tree=%s pull origin %s' % (
                self.path, self.path, self.branch
            )
            return cmd.split()

    def download(self, parent=None, is_loop=False, fetch_dep=True):
        if self.path in ADDONS_PATH:
            return
        if os.path.exists(self.path):
            if fetch_dep:
                print('PULL: %s %s' % (self.path, self.branch))
                cmd = self.update_cmd
                call(cmd)
            else:
                self.fetch_branch_name()
        else:
            print('CLONE: %s %s' % (self.path, self.branch))
            result = call(self.download_cmd)
            if result != 0:
                if parent and parent.parent:
                    self.branch = parent.parent.branch
                    self.download(
                        parent=parent.parent,
                        is_loop=True,
                        fetch_dep=fetch_dep)
                else:
                    self.branch = None
                    self.download(
                        is_loop=True,
                        fetch_dep=fetch_dep)
            else:
                self.fetch_branch_name()

        if not is_loop:
            ADDONS_PATH.append(self.path)
            self.download_dependency(fetch_dep)

    def download_dependency(self, fetch_dep=True):
        filename = '%s/%s' % (self.path, DEPENDENCIES_FILE)
        if not os.path.exists(filename):
            return
        repo_list = []
        with open(filename) as f:
            for line in f:
                l = line.strip('\n').strip()
                if l.startswith('#') or not l:
                    continue
                repo_list.append(Repo(l, self))
        for repo in repo_list:
            repo.download(
                parent=repo.parent,
                fetch_dep=fetch_dep)


def write_addons_path():
    move(ODOO_CONF, OLD_ODOO_CONF)
    with open(ODOO_CONF, 'a') as target_file, open(OLD_ODOO_CONF, 'r') as source_file:
        for line in source_file:
            if not re.match(REGEX_ADDONS_PATH, line):
                target_file.write(line)

        new_line = 'addons_path = %s' % ','.join(list(set(ADDONS_PATH)))
        target_file.write(new_line)

    remove(OLD_ODOO_CONF)


def main():
    fetch_dep = True
    remote_url = None

    # 1st param is FETCH_OCA_DEPENDENCIES
    if len(sys.argv) > 1:
        if str(sys.argv[1]).lower() == 'false':
            fetch_dep = False

    # 2nd param is the ADDONS_REPO
    if len(sys.argv) > 2:
        remote_url = sys.argv[2]

    # If the ADDONS_REPO contains a branch name, there is a space before the
    # branch name so the branch name becomes the 3rd param
    if len(sys.argv) > 3:
        remote_url += ' ' + sys.argv[3]

    if remote_url:
        # Only one master repo to download
        print('remote_url: %s ' % remote_url)
        Repo(remote_url).download(fetch_dep=fetch_dep)
    else:
        # List of repos is defined in oca_dependencies.txt at the root of
        # additional_addons folder, let's download them all
        with open(EXTRA_ADDONS_PATH + DEPENDENCIES_FILE, 'r') as f:
            for line in f:
                l = line.strip('\n').strip()
                if l.startswith('#') or not l:
                    continue
                print('remote_url: %s ' % l)
                Repo(l).download(fetch_dep=fetch_dep)

    write_addons_path()

if __name__ == '__main__':
    main()
