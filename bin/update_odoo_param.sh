#!/bin/bash
#
# FIXME the below code should be in boot but for an unknown reason, the
# instruction `grep` fails to run in boot, when it works fine here.
# Both are bash scripts, but:
#  - boot is run by Docker as an entrypoint
#  - target_user.sh is run using bash command
#
log_src='['${0##*/}']'

odoo_user="$1"
odoo_conf_file="$2"
odoo_param="$3"
val="$4"

# Check if the conf already contains that parameter
grep -q "^$odoo_param\s*=" "$odoo_conf_file"
found="$?"

if [ "$found" -eq 0 ]; then
    # Substitute the value
    sudo -i -u "$odoo_user" sed -i \
        "s/^$odoo_param\s*=.*/$odoo_param = $val/g" "$odoo_conf_file"
else
    # Append the parameter (hide tee output to stdout)
    echo "$odoo_param = $val" | \
        sudo -i -u "$odoo_user" tee -a "$odoo_conf_file" > /dev/null
fi
