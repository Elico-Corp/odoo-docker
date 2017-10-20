# -*- coding: utf-8 -*-
# Copyright 2015 Elico Corp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import os
import re
import shutil
import subprocess
import sys
import urlparse

EXTRA_ADDONS_PATH = '/opt/odoo/additional_addons/'
ODOO_ADDONS_PATH = '/opt/odoo/sources/odoo/addons'
ODOO_CONF = '/opt/odoo/etc/odoo.conf'
DEFAULT_SCHEME = 'https'
DEFAULT_GIT_HOSTING_SERVICE = 'github.com'
DEFAULT_ORGANIZATION = 'OCA'
DEPENDENCIES_FILE = 'oca_dependencies.txt'


class Repo(object):
    """
    Fetch Git repositories recursively.

    Based on the OCA cross repository dependency management system:
    https://github.com/OCA/maintainer-quality-tools/pull/159

    Following the oca_dependencies.txt syntax:
    https://github.com/OCA/maintainer-quality-tools/blob/master/sample_files/oca_dependencies.txt
    """
    def __init__(self, remote_url, fetch_dep, parent=None):
        self.remote_url = remote_url
        self.fetch_dep = fetch_dep
        self.parent = parent

        self.scheme = DEFAULT_SCHEME
        self.netloc = DEFAULT_GIT_HOSTING_SERVICE
        self.organization = DEFAULT_ORGANIZATION
        self.repository = None
        self.branch = parent.branch if parent else None
        self.folder = None

        self._parse()

    @staticmethod
    def _is_http(url):
        # FIXME should also support following syntax (different from Git SSH):
        # 'ssh://git@github.com/organization/private-repo'
        return re.match(r'^https?:/{2}.+', url)

    @staticmethod
    def _is_git_ssh(url):
        return re.match(r'^\w+@\w+\.\w+:.+', url)

    @staticmethod
    def _is_url(url):
        return Repo._is_http(url) or Repo._is_git_ssh(url)

    def _parse_org_repo(self, repo):
        args = repo.split('/')

        if len(args) == 1:
            # Pattern: 'public-repo'
            self.repository = args[0]
        elif len(args) == 2:
            # Pattern: 'organization/public-repo'
            self.organization = args[0]
            self.repository = args[1]
        else:
            print >> sys.stderr, 'FATAL: unexpected repository pattern'
            print >> sys.stderr, 'Expected pattern #1: public-repo'
            print >> sys.stderr, 'Expected pattern #2: organization/public-repo'
            print >> sys.stderr, 'Actual value: %s' % repo

    def _parse_url(self, url):
        path = None

        if Repo._is_http(url):
            # Pattern: 'https://github.com/organization/public-repo'
            parsed_url = urlparse.urlparse(url)

            self.scheme = parsed_url.scheme
            self.netloc = parsed_url.netloc

            if len(parsed_url.path) > 0:
                path = parsed_url.path[1:]
            else:
                print >> sys.stderr, 'FATAL: unexpected repository pattern'
                print >> sys.stderr, 'Expected pattern: https://github.com/organization/public-repo'
                print >> sys.stderr, 'Actual value: %s' % url
                return
        else:
            # Pattern: 'git@github.com:organization/private-repo'
            self.scheme = 'ssh'
            args = url.split(':')

            if len(args) == 2:
                self.netloc = args[0]
                path = args[1]
            else:
                print >> sys.stderr, 'FATAL: unexpected repository pattern'
                print >> sys.stderr, 'Expected pattern: git@github.com:organization/private-repo'
                print >> sys.stderr, 'Actual value: %s' % url
                return

        # Pattern: 'organization/repo'
        args = path.split('/')

        if len(args) == 2:
            self.organization = args[0]
            # Repo might end with '.git' but it's optional
            self.repository = args[1].replace('.git', '')
        else:
            print >> sys.stderr, 'FATAL: unexpected repository pattern'
            print >> sys.stderr, 'Expected pattern: organization/repo' 
            print >> sys.stderr, 'Actual value: %s' % path

    def _parse_repo(self, repo):
        if Repo._is_url(repo):
            self._parse_url(repo)
        else:
            self._parse_org_repo(repo)

    def _parse(self):
        # Clean repo (remove multiple/trailing spaces)
        repo = re.sub('\s+', ' ', self.remote_url.strip())

        # Check if folder and/or branch are provided
        args = repo.split(' ')

        if len(args) == 1:
            # Pattern: 'repo'
            self._parse_repo(repo)
            self.folder = self.repository

        if len(args) == 2:
            if Repo._is_url(args[1]):
                # Pattern: 'folder repo'
                # This pattern is only valid if the repo is a URL
                self._parse_url(args[1])
                self.folder = args[0]
            else:
                # Pattern: 'repo branch'
                self._parse_repo(args[0])
                self.folder = self.repository
                self.branch = args[1]

        elif len(args) == 3:
            # Pattern: 'folder repo branch'
            self._parse_repo(args[1])
            self.folder = args[0]
            self.branch = args[2]

    @property
    def path(self):
        return '%s%s' % (EXTRA_ADDONS_PATH, self.folder)

    @property
    def resolve_url(self):
        return '%s://%s/%s/%s.git' % (
            self.scheme,
            self.netloc,
            self.organization,
            self.repository
        )

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
        return cmd

    @property
    def update_cmd(self):
        cmd = 'git -C %s pull origin %s' % (
            self.path, self.branch
        )
        return cmd

    def _fetch_branch_name(self):
        # Example of output from `git branch` command:
        #   7.0
        #   7.0.1.0
        # * 7.0.1.1
        #   8.0
        #   8.0.1.0
        #   9.0
        #   9.0.1.0
        branch_cmd = 'git -C %s branch' % (
            self.path
        )

        # Search for the branch prefixed with '* '
        try:
            found = False
            output = subprocess.check_output(branch_cmd, shell=True)
            for line in output.split('\n'):
                if line.startswith('*'):
                    self.branch = line.replace('* ', '')
                    found = True
                    break

            if not found:
                print >> sys.stderr, 'FATAL: cannot fetch branch name'
                print >> sys.stderr, 'Path: %s' % self.path

        except Exception, e:
            print >> sys.stderr, 'FATAL: cannot fetch branch name'
            print >> sys.stderr, e

    def _download_dependencies(self, addons_path):
        # Check if the repo contains a dependency file
        filename = '%s/%s' % (self.path, DEPENDENCIES_FILE)
        if not os.path.exists(filename):
            return

        # Download the dependencies
        with open(filename) as f:
            for line in f:
                l = line.strip('\n').strip()
                if l and not l.startswith('#'):
                    Repo(l, self.fetch_dep, self).download(addons_path)

    def download(self, addons_path, parent=None, is_retry=False):

	# No need to fetch a repo twice (it could also cause infinite loop)
        if self.path in addons_path:
            return

        if os.path.exists(self.path):
            # Branch name is used to:
            #  - pull the code
            #  - fetch the child repos
            self._fetch_branch_name()

            if self.fetch_dep:
                # Perform `git pull`
                print 'Pulling: %s' % self.remote_url
                sys.stdout.flush()
                result = subprocess.call(self.update_cmd.split())

                if result != 0:
                    print >> sys.stderr, 'FATAL: cannot git pull repository'
                    print >> sys.stderr, 'URL: %s' % self.remote_url
        else:
            # Perform `git clone`
            print 'Cloning: %s' % self.remote_url
            sys.stdout.flush()
            result = subprocess.call(self.download_cmd.split())

            if result != 0:
                # Since `git clone` failed, try some workarounds
                if parent and parent.parent:
                    # Retry recursively using the ancestors' branch
                    self.branch = parent.parent.branch
                    self.download(
                        addons_path,
                        parent=parent.parent,
                        is_retry=True)
                elif not is_retry:
                    # Retry one last time with the default branch of the repo
                    self.branch = None
                    self.download(addons_path, is_retry=True)
                else:
                    print >> sys.stderr, 'FATAL: cannot git clone repository'
                    print >> sys.stderr, 'URL: %s' % self.remote_url
            else:
                # Branch name is used to fetch the child repos
                self._fetch_branch_name()

        if not is_retry:
            addons_path.append(self.path)
            self._download_dependencies(addons_path)


def write_addons_path(addons_path):
    conf_file = ODOO_CONF + '.new'

    with open(conf_file, 'a') as target, open(ODOO_CONF, 'r') as source:
        # Copy all lines except for the addons_path parameter
        for line in source:
            if not re.match(r'^addons_path\s*=\s*', line):
                target.write(line)

        # Append addons_path
        target.write('addons_path = %s' % ','.join(addons_path))

    shutil.move(conf_file, ODOO_CONF)


def main():
    fetch_dep = True
    remote_url = None
    addons_path = []

    # 1st param is FETCH_OCA_DEPENDENCIES
    if len(sys.argv) > 1:
        if str(sys.argv[1]).lower() == 'false':
            fetch_dep = False

    # 2nd param is the ADDONS_REPO
    if len(sys.argv) > 2:
        remote_url = sys.argv[2]

    if remote_url:
        # Only one master repo to download
        Repo(remote_url, fetch_dep).download(addons_path)
    else:
        # List of repos defined in oca_dependencies.txt at the root of
        # additional_addons folder, download them all
        with open(EXTRA_ADDONS_PATH + DEPENDENCIES_FILE, 'r') as f:
            for line in f:
                l = line.strip('\n').strip()
                if l and not l.startswith('#'):
                    Repo(l, fetch_dep).download(addons_path)

    # Odoo standard addons path must be the last, in case an additional addon
    # uses the same name as a standard module (e.g. Odoo EE 'web' module in v9)
    addons_path.append(ODOO_ADDONS_PATH)

    write_addons_path(addons_path)

if __name__ == '__main__':
    main()

