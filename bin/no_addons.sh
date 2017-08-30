#!/bin/bash
#
# FIXME the below code should be in boot but for an unknown reason, the
# instruction `grep` fails to run in boot, when it works fine here.
# If we remove "^" from the regex, `grep` will run fine in boot!
# Both are bash scripts, but:
#  - boot is run by Docker as an entrypoint
#  - target_user.sh is run using bash command
#
log_src='['${0##*/}']'

odoo_user="$1"
odoo_conf_file="$2"

grep -q '^addons_path\s*=' "$odoo_conf_file"
found="$?"

if [ "$found" -ne 0 ]; then
    # Append the parameter (hide tee output to stdout)
    echo 'addons_path = /opt/odoo/sources/odoo/addons' | \
        sudo -i -u "$odoo_user" tee -a "$odoo_conf_file" > /dev/null
fi
