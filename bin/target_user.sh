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
    # Name of the target Odoo user
    TARGET_USER_NAME='target-odoo-user'

    # Check whether target user exists or not
    exists=$( getent passwd "$TARGET_UID" | wc -l )

    # Create target user
    if [ "$exists" == "0" ]; then
        echo $log_src[`date +%F.%H:%M:%S`]' Creating target Odoo user...'
        odoo_user="$TARGET_USER_NAME"
        adduser --uid "$TARGET_UID" --disabled-login --gecos "" --quiet \
            "$odoo_user"

        # Add target user to odoo group so that he can read/write the content
        # of /opt/odoo
        usermod -a -G odoo "$odoo_user"
    else
        # Target user already exists in the following cases:
        #  1) Mapping with the same UID as odoo, OK
        #  2) Target user has already been created (e.g. container has been
        #     restarted), OK
        #  3) Mapping with another existing user (e.g. root, etc.), not OK
        odoo_user_id=$( id -u "$odoo_user" )
        target_uid_name=$( getent passwd "$TARGET_UID" | cut -d: -f1 )

        if [ "$TARGET_UID" -ne "$odoo_user_id" ] && \
                [ "$TARGET_USER_NAME" != "$target_uid_name" ]; then
            echo $log_src[`date +%F.%H:%M:%S`]' ERROR: Cannot create target' \
                'user as target UID already exists.'
            exit 1
        fi
    fi
fi

# Return target Odoo user to boot script
echo "$odoo_user" > /tmp/odoo_user
