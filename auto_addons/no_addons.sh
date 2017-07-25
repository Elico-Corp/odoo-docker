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

grep -P "^addons_path\s*=" $1
if [ $? -ne 0 ]; then
    echo "addons_path = /opt/odoo/sources/odoo/addons" >> $1
fi