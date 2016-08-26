# -*- coding: utf-8 -*-
# Copyright 2015 Elico Corp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re

ODOO_CONF = '/opt/odoo/etc/odoo.conf'


def main():
    contains_addons_path = False
    with open(ODOO_CONF, 'r') as conf_file:
        for line in conf_file:
            if re.match(r'^addons_path*=*', line):
                contains_addons_path = True
                break
    conf_file.close()

    if not contains_addons_path:
        print('ADDED default addons_path in odoo.conf')
        with open(ODOO_CONF, 'a') as conf_file:
            conf_file.write(
                'addons_path = /opt/odoo/sources/odoo/addons'
            )

    conf_file.close()

if __name__ == '__main__':
    main()
