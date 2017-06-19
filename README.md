# odoo-docker
Docker files to build dockers based on:
* standard Odoo code
* OCB code

This work is original based on the docker from http://www.xcg-consulting.fr and available here:
https://hub.docker.com/r/xcgd/odoo/

# Roadmap
* Instead of having a predefined list of odoo.conf parameters available as ENV variables, allow
  to change any of them dynamically. Suggested solution:
  * pattern for ENV variable: "ODOO_CONF_" + parameter + "=" + value, e.g.:
    * ODOO_CONF_dbfilter=^stable_.*
    * ODOO_CONF_db_user=odoo
    * ODOO_CONF_limit_memory_soft=671088640
  * then, in the boot script:
    * loop over each parameter of odoo.conf
    * check if there's an ENV variable "ODOO_CONF_" + parameter
    * if so, replace the parameter in odoo.conf
* Allow pulling GitHub repos using an oca_dependencies.txt file rather than the ENV variable
  $ADDONS_REPO. This way, it will be possible to pull multiple repos not necessarily linked to
  each other (e.g. OCA/business_requirements and odoo_enterprise)