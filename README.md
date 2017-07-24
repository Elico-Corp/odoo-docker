# odoo-docker
Docker files to build dockers based on:
* standard Odoo code
* OCB code

This work is original based on the docker from http://www.xcg-consulting.fr and available here: https://hub.docker.com/r/xcgd/odoo/

oca_dependencies.txt

For public repo:
* oca-repo -> https://github.com/OCA/oca-repo (default branch)
* oca-repo 8.0 -> https://github.com/OCA/oca-repo (branch: 8.0)
* organization/public-repo -> https://github.com/organization/public-repo (default branch)
* organization/public-repo 8.0 -> https://github.com/organization/public-repo (branch: 8.0)
* https://github.com/organization/public-repo -> https://github.com/organization/public-repo (default branch)
* https://github.com/organization/public-repo 8.0 -> https://github.com/organization/public-repo (branch: 8.0)
* public_repo_rename https://github.com/organization/public-repo -> https://github.com/organization/public-repo (default branch)
* public_repo_rename https://github.com/organization/public-repo 8.0 -> https://github.com/organization/public-repo (branch: 8.0)

For private repo:
* git@github.com:Elico-Corp/private-repo
* git@github.com:Elico-Corp/private-repo 8.0
* private_repo_rename git@github.com:Elico-Corp/private-repo
* private_repo_rename git@github.com:Elico-Corp/private-repo 8.0

Usage:

config docker-compose.yml

volumes:
* ./volumes/odoo/[project name]/odoo_data:/opt/odoo/data/filestore
* ./volumes/odoo/[project name]/extra_addons:/opt/odoo/additional_addons
* ./volumes/odoo/[project name]/ssh:/mnt/ssh

environment:
* ADDONS_REPO=git@github.com:xxx/xxx
* FETCH_OCA_DEPENDENCIES=False
* ADMIN_PASSWORD=xxx
* DB_USER=xxx
* DB_PASSWORD=xxx
* DB_FILTER=^xxx.*
