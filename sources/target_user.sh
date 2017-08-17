#!/bin/bash
#
# FIXME the below code should be in boot but for an unknown reason, the
# instruction `getent passwd` fails to run in boot, when it works fine here.
# Both are bash scripts, but:
#  - boot is run by Docker as an entrypoint
#  - target_user.sh is run using bash command
#
log_src='['${0##*/}']'

# Check if there's a target user to run Odoo
if [ "$TARGET_ID" ]; then
    echo $log_src[`date +%F.%H:%M:%S`]' Check if target user exists...'
    EXISTS=$( getent passwd $TARGET_ID | wc -l )

    # Create target user
    if [ $EXISTS == "0" ]; then
        echo $log_src[`date +%F.%H:%M:%S`]' Create target user...'
        adduser --uid $TARGET_ID --disabled-password --gecos "" --shell=/bin/bash target-user

        # Add target user to odoo group so that he can read/write the content of /opt/odoo
        echo $log_src[`date +%F.%H:%M:%S`]' Add target user to odoo group...'
        usermod -a -G odoo target-user
    # If the user already exists, check if it's the same as odoo
    else
        echo $log_src[`date +%F.%H:%M:%S`]' Target user already exists, make sure it is odoo...'
        ODOO_ID=$( id -u odoo )
        if [ $TARGET_ID -ne $ODOO_ID ]; then
            echo $log_src[`date +%F.%H:%M:%S`]' The target user is not the same as odoo, exiting'
            exit 1
        fi
    fi
fi
