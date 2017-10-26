# elicocorp/odoo
Simple yet powerful [Odoo][odoo] image for [Docker][dk] maintained by
[Elico Corporation][ec].

  [odoo]: https://www.odoo.com/
  [dk]: https://www.docker.com/
  [ec]: https://www.elico-corp.com/

<a name="toc"></a>
## Table of Contents
- [Usage](#usage)
    - [Run the image](#run_image)
    - [Compose example](#compose_example)
- [Security](#security)
- [Data persistency](#data_persistency)
- [Host user mapping](#host_user_mapping)
    - [Default host user mapping in Docker](#default_hum)
    - [Host user mapping and volumes](#hum_and_volumes)
    - [Impact](#impact)
    - [Solution](#solution)
- [Odoo configuration file](#odoo_conf)
- [Additional Odoo modules](#additional_addons)
    - [Automatically fetch Git repositories](#git_fetch)
    - [Fetch multiple independent repositories](#fetch_multiple_repos)
    - [Fetch private GitHub repositories](#git_ssh)
- [Run a bash script at startup](#startup_script)
- [How to extend this image](#extend_image)
- [Roadmap](#roadmap)
- [Bug Tracker](#bug_tracker)
- [Credits](#credits)
    - [Contributors](#contributors)
    - [Maintainer](#maintainer)

  [toc]: #toc "Table of Contents"

<a name="usage"></a>
## Usage[^][toc]
In order to use this image, a recent version of Docker must be installed on the
host. For more information about Docker Engine, see the
[official documentation][dk-doc].

  [dk-doc]: https://docs.docker.com/engine/

<a name="run_image"></a>
### Run the image[^][toc]
Running this image without specifying any command will display this help
message:

    $ docker run elicocorp/odoo:10.0

To display the user manual, run the image with the command `man`. Redirecting
`stdout` to `less` is highly recommended:

    $ docker run elicocorp/odoo:10.0 man | less

To start Odoo, run the image with the command `start`:

    $ docker run elicocorp/odoo:10.0 start

The easiest way to use this image is to run it along with a [PostgreSQL][pg]
image. By default, Odoo is configured to connect with a PostgreSQL host named
`db`.

  [pg]: https://hub.docker.com/_/postgres/

**Note:** The [PostgreSQL image][ec-pg] of Elico Corp can be used as well.

  [ec-pg]: https://hub.docker.com/r/elicocorp/postgres/

<a name="compose_example"></a>
### Compose example[^][toc]
Below is an example of a simple `docker-compose.yml` to use this image. For
more information about Compose, see the [official documentation][dc-doc].

  [dc-doc]: https://docs.docker.com/compose/

    version: '3.3'
    services:

      postgres:
        image: postgres:9.5
        environment:
          - POSTGRES_USER=odoo

      odoo:
        image: elicocorp/odoo:10.0
        command: start
        ports:
          - 127.0.0.1:8069:8069
        links:
          - postgres:db
        environment:
          - ODOO_DB_USER=odoo

Once this file is created, simply move to the corresponding folder and run the
following command to start Odoo:

    $ docker-compose up

**Note 1:** With this configuration, Odoo will be accessible at the following
URL *only* from the local host: <http://127.0.0.1:8069>

It is possible to publish it following one of these options:

1. map a reverse-proxy to `127.0.0.1:8069`
2. remove the `127.0.0.1:` prefix in order to publish the port `8069` outside
the local host

**Note 2:** With this configuration:

1. Odoo is running without master password
2. `odoo` PostgreSQL user is a superuser who doesn't require any password

See [Security](#security) section for more info.

**Note 3:** With this configuration, all the data will be lost once the
[containers][dk-con] are stopped.

  [dk-con]: https://www.docker.com/what-container
            "What is a Container | Docker"

See [Data persistency](#data_persistency) section for more info.

<a name="security"></a>
## Security[^][toc]
In order to improve the security, it is recommended to:

1. set a master password for Odoo using `ODOO_ADMIN_PASSWD`
2. start PostgreSQL with a different superuser (e.g. `postgres`)
3. give the superuser a password using `POSTGRES_PASSWORD`
4. create a separate PostgreSQL user for Odoo (e.g. `odoo`) with his own
password and specify it using `ODOO_DB_PASSWORD`

**Note:** Run below SQL queries with PostgreSQL superuser to create the `odoo`
user:

    CREATE user odoo WITH password 'strong_pg_odoo_password';
    ALTER user odoo WITH createdb;

The `docker-compose.yml` should look like:

    version: '3.3'
    services:

      postgres:
        image: postgres:9.5
        environment:
          - POSTGRES_USER=postgres
          - POSTGRES_PASSWORD=strong_pg_superuser_password

      odoo:
        image: elicocorp/odoo:10.0
        command: start
        ports:
          - 127.0.0.1:8069:8069
        links:
          - postgres:db
        environment:
          - ODOO_ADMIN_PASSWD=strong_odoo_master_password
          - ODOO_DB_USER=odoo
          - ODOO_DB_PASSWORD=strong_pg_odoo_password

**Note:** If Odoo is behind a reverse proxy, it is also suggested to change the
port published by the container (though this port is actually not opened to the
outside). For instance:

        ports:
          - 127.0.0.1:12345:8069

<a name="data_persistency"></a>
## Data persistency[^][toc]
As soon as the containers are removed, all the modifications (e.g. database,
attachments, etc.) will be lost. There are 2 main [volumes][dk-vol] that must
be made persistent in order to preserve the data:

  [dk-vol]: https://docs.docker.com/engine/admin/volumes/volumes/
            "Use volumes | Docker Documentation"

1. the PostgreSQL database in `/var/lib/postgresql/data`
2. the Odoo filestore in `/opt/odoo/data/filestore`

Optionally, it is also possible to map the Odoo sessions folder in
`/opt/odoo/data/sessions`

In the following example, these volumes are mapped under the folder `volumes`
which is in the same folder as the `docker-compose.yml`. This command will
create the corresponding folders:

    mkdir -p ./volumes/{postgres,odoo/filestore,odoo/sessions}

The `docker-compose.yml` should look like:

    version: '3.3'
    services:

      postgres:
        image: postgres:9.5
        volumes:
          - ./volumes/postgres:/var/lib/postgresql/data
        environment:
          - POSTGRES_USER=postgres
          - POSTGRES_PASSWORD=strong_pg_superuser_password

      odoo:
        image: elicocorp/odoo:10.0
        command: start
        ports:
          - 127.0.0.1:8069:8069
        links:
          - postgres:db
        volumes:
          - ./volumes/odoo/filestore:/opt/odoo/data/filestore
          - ./volumes/odoo/sessions:/opt/odoo/data/sessions
        environment:
          - ODOO_ADMIN_PASSWD=strong_odoo_master_password
          - ODOO_DB_USER=odoo
          - ODOO_DB_PASSWORD=strong_pg_odoo_password

**Note:** With this configuration, all the data created in the volumes will
belong to the user whose UID matches the user running inside the container.

See Host user mapping section for more info.

<a name="host_user_mapping"></a>
## Host user mapping[^][toc]

<a name="default_hum"></a>
### Default host user mapping in Docker[^][toc]
Each Docker image defines its own [users][dk-user]. Users only exist inside the
running container.

  [dk-user]: https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/#user

For instance:

* in `elicocorp/odoo` image, the default user that will run the Odoo process is
`odoo` with UID `1000`
* in `postgres` image, the default user that will run the PostgreSQL process is
`postgres` with UID `999`

Whenever those users are used inside the container, Docker will actually use
the corresponding user on the host running Docker. The mapping is made on the
UID, not on the user name.

If the user `elico` with UID `1000` exists on the host, when running the Odoo
image with the default user, the Odoo process executed by the `odoo` user
inside the container will actually be executed by the host user `elico`.

**Note:** The users don't have to actually exist on the host for the container
to use them. Anonymous users with the corresponding UID will be created
automatically.

If the with UID `999` doesn't exist on the host, when running the PostgreSQL
image with the default user, the PostgreSQL process executed by the `postgres`
user inside the container will actually be executed by the anonymous host user
with UID `999`.

<a name="hum_and_volumes"></a>
### Host user mapping and volumes[^][toc]
When the user inside the container owns files that belong to a volume, the
corresponding files in the folder mapped to the volume on the host will
actually belong to the corresponding user on the host.

Following the previous example:

* in the Odoo container, the files created by the `odoo` user in the folder
`/opt/odoo/data/filestore` will be stored on the host in the folder
`./volumes/odoo/filestore` and belong to the host user `elico`
* in the PostgreSQL container, the files created by the `postgres` user in the
folder `/var/lib/postgresql/data` will be stored on the host in the folder
`./volumes/postgres` and belong to the anonymous host user with UID `999`

<a name="impact"></a>
### Impact[^][toc]
When having `root` privileges on the host, the default host user mapping
behavior is usually not a big issue. The main impact is that the files mapped
with a volume might belong to users that don't have anything to do with the
corresponding Docker services.

In the previous example:

* the host user `elico` will be able to read the content of the Odoo filestore
* the anonymous host user with UID `999` will be able to read the PostgreSQL
database files

It is possible to avoid this by creating host users with the corresponding UIDs
in order to control which host user owns the files in a volume.

However, a user with limited system privileges (e.g. no `sudo`) will have a
bigger issue. The typical use case is a user with limited system privileges
that maps a volume inside his home folder. He would expect to own all the files
under his home folder, which won't be the case.

Following the previous example, if the host user `seb` with UID `1001` starts
the image from his home folder:

* the files in `./volumes/odoo/filestore` will belong to the host user `elico`
* the files in `./volumes/postgres` will belong to the anonymous host user with
UID `999`

The host user `seb` will not be able to access those files even though they are
located under his own home folder. This can lead to very annoying situations
where a user would require the system administrator to help him delete files
under his own home folder.

<a name="solution"></a>
### Solution[^][toc]
Each Docker image has its own way to deal with host user mapping:

* for PostgreSQL, see the [official documentation][pg] (section "Arbitrary
--user Notes")
* for this image, use the environment variable `TARGET_UID` as described below

First, the host user needs to find out his UID:

    $ echo $UID

Then, simply assign this UID to the environment variable `TARGET_UID`.

After starting the Docker containers, all the files created in the volumes will
belong to the corresponding host user.

The `docker-compose.yml` should look like:

    version: '3.3'
    services:

      postgres:
        image: postgres:9.5
        volumes:
          - ./volumes/postgres:/var/lib/postgresql/data
          - /etc/passwd:/etc/passwd:ro
        environment:
          - POSTGRES_USER=postgres
          - POSTGRES_PASSWORD=strong_pg_superuser_password
        user: 1001:1001

      odoo:
        image: elicocorp/odoo:10.0
        command: start
        ports:
          - 127.0.0.1:8069:8069
        links:
          - postgres:db
        volumes:
          - ./volumes/odoo/filestore:/opt/odoo/data/filestore
          - ./volumes/odoo/sessions:/opt/odoo/data/sessions
        environment:
          - TARGET_UID=1001
          - ODOO_ADMIN_PASSWD=strong_odoo_master_password
          - ODOO_DB_USER=odoo
          - ODOO_DB_PASSWORD=strong_pg_odoo_password

**Note:** For a more dynamic UID mapping, you can use Compose
[variable substitution][dk-var]. Simply export the environment variable `UID`
before starting the container and replace the `UID` with `$UID` in the
`docker-compose.yml`.

  [dk-var]: https://docs.docker.com/compose/compose-file/#variable-substitution

<a name="odoo_conf"></a>
## Odoo configuration file[^][toc]
The configuration file is generated automatically at startup. Any available
Odoo parameter can be provided as an environment variable, prefixed by `ODOO_`.

**Note:** As a convention, it is preferrable to use only big caps but this is
not mandatory. The parameters will be converted to small caps in the
configuration file.

In the previous `docker-compose.yml` examples, the following Odoo parameters
have already been defined:

* `admin_passwd`: environment variable `ODOO_ADMIN_PASSWD`
* `db_user`: environment variable `ODOO_DB_USER`
* `db_password`: environment variable `ODOO_DB_PASSWORD`

For a complete list of Odoo parameters, see the [documentation][od-par].

  [od-par]: https://www.odoo.com/documentation/10.0/reference/cmdline.html

It is also possible to use a custom Odoo configuration file. The most common
ways are:

1. [`ADD`][dk-add] the configuration file in `/opt/odoo/etc/odoo.conf` using a
[`Dockerfile`][dkf]
2. Map the `/opt/odoo/etc/odoo.conf` using a volume

  [dk-add]: https://docs.docker.com/engine/reference/builder/#add
  [dkf]: https://docs.docker.com/engine/reference/builder/
         "Dockerfile reference | Docker Documentation"

<a name="additional_addons"></a>
## Additional Odoo modules[^][toc]
This image allows to load additional Odoo modules through the volume
`/opt/odoo/additional_addons`. When adding modules manually in that folder, the
Odoo parameter `addons_path` must be defined accordingly:

    addons_path = /opt/odoo/additional_addons,/opt/odoo/sources/odoo/addons

**Note:** The previous configuration assumes that all the modules are at the
root of the folder `/opt/odoo/additional_addons`. Depending on the folder
structure, the parameter might need to be adapted.

<a name="git_fetch"></a>
### Automatically fetch Git repositories[^][toc]

This image is able to automatically fetch (e.g. `git clone`) a [Git][git]
repository containing a set of modules. It is based on the
[cross repository dependency management][cross-repo-dep] system introduced by
the [OCA][oca].

  [git]: https://git-scm.com
  [cross-repo-dep]: https://github.com/OCA/maintainer-quality-tools/pull/159
  [oca]: https://github.com/OCA/ "Odoo Community Association"

Basically, this image is able to recursively fetch Git repositories in the
`/opt/odoo/additional_addons` volume. Once all the repositories have been
fetched, the `addons_path` parameter will be generated automatically.

The cross repository dependency is based on the
[`oca_dependencies.txt`][oca-dep] syntax.

  [oca-dep]: https://github.com/OCA/maintainer-quality-tools/blob/master/sample_files/oca_dependencies.txt

**Note:** This image integrates a Git repositories cache system. If some of the
repositories already exist in the volume (e.g. when restarting the container),
the container will pull (e.g. `git pull`) them instead of cloning them, which
allows for much faster boot.

The easiest way to clone a Git repository is to set the environment variable
`ADDONS_REPO` with the URL of the repository.

For instance, in order to fetch the [OCA Project][oca-project] Git repository,
as well as all the Git repositories it depends on, you can use the following
`docker-compose.yml`:

  [oca-project]: https://github.com/OCA/project
                 "Odoo Project Management and Services Company Addons"

    version: '3.3'
    services:

      postgres:
        image: postgres:9.5
        volumes:
          - ./volumes/postgres:/var/lib/postgresql/data
          - /etc/passwd:/etc/passwd:ro
        environment:
          - POSTGRES_USER=postgres
          - POSTGRES_PASSWORD=strong_pg_superuser_password
        user: 1001:1001

      odoo:
        image: elicocorp/odoo:10.0
        command: start
        ports:
          - 127.0.0.1:8069:8069
        links:
          - postgres:db
        volumes:
          - ./volumes/odoo/addons:/opt/odoo/additional_addons
          - ./volumes/odoo/filestore:/opt/odoo/data/filestore
          - ./volumes/odoo/sessions:/opt/odoo/data/sessions
        environment:
          - ADDONS_REPO=https://github.com/OCA/project.git
          - TARGET_UID=1001
          - ODOO_ADMIN_PASSWD=strong_odoo_master_password
          - ODOO_DB_USER=odoo
          - ODOO_DB_PASSWORD=strong_pg_odoo_password

**Note:** After the repositories have been fetched, it might not be required to
pull them every time the container is restarted. In that case, simply set the
environment variable `FETCH_OCA_DEPENDENCIES` to `False` (default value is
`True`) in order to boot much faster, e.g.:

    environment:
      - FETCH_OCA_DEPENDENCIES=False

<a name="fetch_multiple_repos"></a>
### Fetch multiple independent repositories[^][toc]
It might be necessary to fetch more than one Git repository (and the
repositories it depends on). In that case, instead of using the `ADDONS_REPO`
environment variable, simply create one `oca_dependencies.txt` file and put it
at the root of the `/opt/odoo/additional_addons` volume.

For instance, if you want to fetch the
[OCA account payment modules][oca-account-payment] repository along with the
OCA project repository, put the following `oca_dependencies.txt` in the
`/opt/odoo/additional_addons` volume:

  [oca-account-payment]: https://github.com/OCA/account-payment

    # list the OCA project dependencies, one per line
    # add a github url if you need a forked version
    project https://github.com/OCA/project.git
    account-payment https://github.com/OCA/account-payment.git

<a name="git_ssh"></a>
### Fetch private GitHub repositories[^][toc]
This image is able to pull multiple private GitHub repositories when provided a
valid SSH key that has read access to these repositories. The URL for GitHub
SSH authentication is available under the "Clone with SSH" option.

Simply put the SSH private key whose name must be `id_rsa` in the volume
`/opt/odoo/ssh`. Since Odoo doesn't need to write in that volume, you can use
the `ro` option to mount a [read-only volume][dk-ro-vol].

  [dk-ro-vol]: https://docs.docker.com/engine/admin/volumes/volumes/#use-a-read-only-volume

The `docker-compose.yml` should look like:

    version: '3.3'
    services:

      postgres:
        image: postgres:9.5
        volumes:
          - ./volumes/postgres:/var/lib/postgresql/data
          - /etc/passwd:/etc/passwd:ro
        environment:
          - POSTGRES_USER=postgres
          - POSTGRES_PASSWORD=strong_pg_superuser_password
        user: 1001:1001

      odoo:
        image: elicocorp/odoo:10.0
        command: start
        ports:
          - 127.0.0.1:8069:8069
        links:
          - postgres:db
        volumes:
          - ./volumes/odoo/addons:/opt/odoo/additional_addons
          - ./volumes/odoo/filestore:/opt/odoo/data/filestore
          - ./volumes/odoo/sessions:/opt/odoo/data/sessions
          - ./volumes/odoo/ssh:/opt/odoo/ssh:ro
        environment:
          - ADDONS_REPO=git@github.com:Elico-Corp/odoo-private-addons.git
          - TARGET_UID=1001
          - ODOO_ADMIN_PASSWD=strong_odoo_master_password
          - ODOO_DB_USER=odoo
          - ODOO_DB_PASSWORD=strong_pg_odoo_password

**Note:** If the host user has a valid SSH key under the `.ssh` folder of his
home folder, he can map his `.ssh` folder instead, e.g.:

    volumes:
      - ~/.ssh:/opt/odoo/ssh:ro

<a name="startup_script"></a>
## Run a bash script at startup[^][toc]
In some cases, it might be useful to run some commands in the container before
starting Odoo. After the Odoo target user has been created, the container will
execute a [bash][bash] script with the container user `root`.

  [bash]: https://www.gnu.org/software/bash/ "GNU Bash"

The script is located at `/opt/scripts/startup.sh` and can be mapped with a
volume or added via a `Dockerfile`.

<a name="extend_image"></a>
## How to extend this image[^][toc]
This image comes with all the dependencies required to run the standard version
of Odoo. However, some additionnal modules might require an extra setup.

While the startup script is a way to achieve this, the changes it operates in
the OS of the container are not persistent. Such setup would be performed every
time the container is restarted, which could induce long delay in the boot
process.

In order to make those changes persistent, simply create a child Docker image
by extending this image.

The below example shows how to install the dependencies `captcha` and
`simplecrypt` for the Odoo v8 module [`website_captcha_nogoogle`][wcn].

  [wcn]: https://github.com/Elico-Corp/odoo-addons/tree/8.0/website_captcha_nogoogle

This is how the `Dockerfile` would look like:

    FROM elicocorp/odoo:8.0
    MAINTAINER Elico Corp <webmaster@elico-corp.com>
    RUN pip install --upgrade cffi
    RUN pip install captcha simple-crypt recaptcha-client
    RUN pip install --upgrade pillow

Save it as `./build/odoo/Dockerfile`. Then, in `docker-compose.yml`, replace
the `image` instruction with a `build` instruction, e.g.:

    odoo:
      build: ./build/odoo

When starting the container with `docker-compose up`, Docker will first build
the image. In order to re-build the `odoo` image, use:

    $ docker-compose build odoo

**Note:** Extend an image is an extremely versatile feature of Docker. The only
limit is your imagination! For instance, check out the Elico Corp Odoo Docker
image [localized for China][odoo-china].

  [odoo-china]: https://github.com/Elico-Corp/odoo-docker-china

<a name="roadmap"></a>
## Roadmap[^][toc]

* Use the code of `maintainer-quality-tools` to pull the `oca_dependencies.txt`

<a name="bug_tracker"></a>
## Bug Tracker[^][toc]
Bugs are tracked on [GitHub Issues][gh-issues]. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

  [gh-issues]: https://github.com/Elico-Corp/elico_odoo/issues

<a name="credits"></a>
## Credits[^][toc]

<a name="contributors"></a>
### Contributors[^][toc]

* Sebastien Maillard <sebastien.maillard@elico-corp.com>
* Eric Caudal <eric.caudal@elico-corp.com>
* Noah Wang <noah.wang@elico-corp.com>
* Augustin Cisterne-Kaas <augustin.cisternekaas@elico-corp.com>

<a name="maintainer"></a>
### Maintainer[^][toc]

[![Elico Corp][ec-logo]][ec]

  [ec-logo]: https://www.elico-corp.com/logo.png

This project is maintained by Elico Corporation.

Elico Corp is an innovative actor in China, Hong-Kong and Singapore servicing
well known international companies and as well as local mid-sized businesses.
Since 2010, our seasoned Sino-European consultants have been providing full
range Odoo services:

* Business consultancy for Gap analysis, BPM, operational work-flows review. 
* Ready-to-use ERP packages aimed at starting businesses.
* Odoo implementation for manufacturing, international trading, service industry
  and e-commerce. 
* Connectors and integration with 3rd party software (Magento, Taobao, Coswin,
  Joomla, Prestashop, Tradevine etc...).
* Odoo Support services such as developments, training, maintenance and hosting.

Our headquarters are located in Shanghai with branch in Singapore servicing
customers from all over Asia Pacific.

Contact information: Sales <contact@elico-corp.com>
