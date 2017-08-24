#!/bin/bash
#
# FIXME the below code should be in boot but for an unknown reason, the
# instruction `getent passwd` fails to run in boot, when it works fine here.
# Both are bash scripts, but:
#  - boot is run by Docker as an entrypoint
#  - target_user.sh is run using bash command
#
log_src='['${0##*/}']'

odoo_user='odoo'

# Check if there's a target user to run Odoo
if [ "$TARGET_UID" ]; then
    # Check whether target user exists or not
    exists=$( getent passwd $TARGET_UID | wc -l )

    # Create target user
    if [ $exists == "0" ]; then
        echo $log_src[`date +%F.%H:%M:%S`]' Creating target Odoo user...'
        odoo_user='target-odoo-user'
        adduser --uid $TARGET_UID --disabled-login --gecos "" $odoo_user

        # Add target user to odoo group so that he can read/write the content
        # of /opt/odoo
        echo $log_src[`date +%F.%H:%M:%S`]' Adding user to `odoo` group...'
        usermod -a -G odoo $odoo_user
    else
        # Target user already exists, make sure it's odoo
        odoo_user_id=$( id -u $odoo_user )

        # If the user already exists, check if it's the same as odoo
        if [ $TARGET_UID -ne $odoo_user_id ]; then
            echo $log_src[`date +%F.%H:%M:%S`]' ERROR: The UID of the target' \
                'user already exists but it is not the same as the ID of' \
                '`odoo` user'
            exit 1
        fi
    fi
fi

# Return target Odoo user to boot script
echo $odoo_user > /tmp/odoo_user
