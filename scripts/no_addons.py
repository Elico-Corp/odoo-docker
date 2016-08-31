# -*- coding: utf-8 -*-
# Copyright 2015 Elico Corp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re
from .addons import ODOO_CONF, REGEX_ADDONS_PATH

DEFAULT_ADDONS_PATH = 'addons_path = /opt/odoo/sources/odoo/addons'


def main():
    contains_addons_path = False
    with open(ODOO_CONF, 'r') as conf_file:
        for line in conf_file:
            if re.match(REGEX_ADDONS_PATH, line):
                contains_addons_path = True
                break
    conf_file.close()

    if not contains_addons_path:
        print('ADDED default addons_path in odoo.conf')
        with open(ODOO_CONF, 'a') as conf_file:
            conf_file.write(DEFAULT_ADDONS_PATH)

    conf_file.close()

if __name__ == '__main__':
    main()
