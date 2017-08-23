# elicocorp/odoo
Simple yet powerful Odoo image for Docker based on [OCB][ocb] code and
maintained by [Elico Corp][ec].

  [ocb]: https://github.com/OCA/OCB "Odoo Community Backports"
  [ec]: https://www.elico-corp.com/

This image is a fork of [XCG Consulting][xcg] Odoo Docker image available
[here][xcgd].

  [xcg]: https://www.xcg-consulting.fr/
  [xcgd]: https://hub.docker.com/r/xcgd/odoo/

## Usage
In order to use this image, a recent version of [Docker][dk] must be installed
on the target host. For more information about Docker Engine, see the
[documentation][dk-doc].

  [dk]: https://www.docker.com/
  [dk-doc]: https://docs.docker.com/engine/

Running this image without specifying a command will display this help message:

    docker run elicocorp/odoo:10.0

The easiest way to use this image is to run it along with a [PostgreSQL][pg]
image.

  [pg]: https://hub.docker.com/_/postgres/

**Note:** The [PostgreSQL image][ec-pg] of Elico Corp can be used as well.

  [ec-pg]: https://hub.docker.com/r/elicocorp/postgres/

Below is an example of a simple `docker-compose.yml` to use this image.
For more information about Docker Compose, see the [documentation][dc-doc].

  [dc-doc]: https://docs.docker.com/compose/

    version: '3.3'
    services:

      postgres:
        image: postgres:9.5
        environment:
          - POSTGRES_USER=odoo
        network_mode: bridge

      odoo:
        image: elicocorp/odoo:10.0
        command: start
        ports:
          - 127.0.0.1:8069:8069
        links:
          - postgres:db
        environment:
          - ODOO_DB_USER=odoo
        network_mode: bridge

**Note 1:** With this configuration, Odoo will be accessible at the following
URL *only* from the local host: <http://127.0.0.1:8069>

It is possible to publish it following one of these options:

1. map a reverse-proxy to `127.0.0.1:8069`
2. remove the `127.0.0.1:` prefix in order to publish the port `8069` outside
the local host

**Note 2:** With this configuration:

1. Odoo is running without master password
2. `odoo` PostgreSQL user is a superuser who doesn't require any password

See Security section for more info.

**Note 3:** With this configuration, all the data will be lost once the
[containers][dk-con] are stopped.

  [dk-con]: https://www.docker.com/what-container
            "What is a Container | Docker"

See Data persistency section for more info.

## Security
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
        network_mode: bridge

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
        network_mode: bridge

**Note:** If Odoo is behind a reverse proxy, it is also suggested to change the
port published by the container (though this port is actually not opened to the
outside). For instance:

        ports:
          - 127.0.0.1:12345:8069

## Data persistency
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
        environment:
          - POSTGRES_USER=postgres
          - POSTGRES_PASSWORD=strong_pg_superuser_password
        volumes:
          - ./volumes/postgres:/var/lib/postgresql/data
        network_mode: bridge

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
        volumes:
           - ./volumes/odoo/filestore:/opt/odoo/data/filestore
           - ./volumes/odoo/sessions:/opt/odoo/data/sessions
        network_mode: bridge

**Note:** With this configuration, all the data created in the volumes will
belong to the user whose UID matches the user running inside the container.

See Host user mapping section for more info.

## Host user mapping

### Default host user mapping in Docker
Each Docker image defines its own [users][dk-user].

  [dk-user]: https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/#user

For instance:

* in `elicocorp/odoo` image, the default user that will run the Odoo process is
`odoo` with UID `1000`
* in `postgres` image, the default user that will run the PostgreSQL process is
`postgres` with UID `999`

Whenever those users are used inside the container, Docker will actually use
the corresponding user on the host running Docker. The mapping is made on the
UID, not on the user name.

For instance, if the user `elico` with UID `1000` exists on the host, when
running the Odoo image with the default user, the Odoo process executed by the
`odoo` user inside the container will actually be executed by the host user
`elico`.

**Note:** The users don't have to actually exist on the host for the container
to use them. Anonymous users with the corresponding UID will be created
automatically.

For instance, if the with UID `999` doesn't exist on the host, when running the
PostgreSQL image with the default user, the PostgreSQL process executed by the
`postgres` user inside the container will actually be executed by the anonymous
host user with UID `999`.

### Host user mapping and volumes
When the user inside the container owns files that belong to a volume, the
corresponding files in the folder mapped to the volume on the host will
actually belong to the corresponding user on the host.

For instance, in the previous example:

* in the Odoo container, the files created by the `odoo` user in the folder
`/opt/odoo/data/filestore` will be stored on the host in the folder
`./volumes/odoo/filestore` and belong to the host user `elico`
* in the PostgreSQL container, the files created by the `postgres` user in the
folder `/var/lib/postgresql/data` will be stored on the host in the folder
`./volumes/postgres` and belong to the anonymous host user with UID `999`

### Impact
When having `root` privileges on the host, the default host user mapping
behavior is usually not a big issue. The main impact is that the files mapped
with a volume might belong to users that don't have anything to do with the
corresponding Docker services.

For instance, in the previous example:

* the host user `elico` will be able to read the content of the Odoo filestore
* the anonymous host user with UID `999` will be able to read the PostgreSQL
database files

It is possible to avoid this by creating host users with the corresponding UIDs
in order to control which host user owns the files in a volume.

However, a user with limited system privileges (e.g. no `sudo`) will have a
bigger issue. The typical use case is a developer with limited system
privileges that maps a volume inside his home folder. He would expect to own
all the files under his home folder, which won't be the case.

For instance, following the previous example, if the host user `seb` with UID
`1001` starts the image from his home folder:

* the files in `./volumes/odoo/filestore` will belong to the host user `elico`
* the files in `./volumes/postgres` will belong to the anonymous host user with
UID `999`

The host user `seb` will not be able to access those files even though they are
located under his own home folder. This can lead to very annoying situations
where a developer would require the system administrator to delete files under
his own home folder.

### Solution
TODO

## Odoo configuration file
The configuration file is generated automatically at startup. Any available
Odoo parameter can be provided as an environment variable, prefixed by `ODOO_`.

**Note:** As a convention, it is preferrable to use only big caps but this is
not mandatory. The parameters will be converted to small caps in the
configuration file.

In the previous `docker-compose.yml` examples, the following Odoo parameters
have already been defined:

* `admin_passwd` (environment variable `ODOO_ADMIN_PASSWD`)
* `db_user` (environment variable `ODOO_DB_USER`)
* `db_password` (environment variable `ODOO_DB_PASSWORD`)

For a complete list of Odoo parameters, see the [documentation][od-par].

  [od-par]: https://www.odoo.com/documentation/10.0/reference/cmdline.html

It is also possible to use a custom Odoo configuration file. The most common
ways are:

1. `ADD` the configuration file in `/opt/odoo/etc/odoo.conf` using a
[Dockerfile][dkf]
2. Map the `/opt/odoo/etc/odoo.conf` using a [volume][dk-vol]

  [dkf]: https://docs.docker.com/engine/reference/builder/
         "Dockerfile reference | Docker Documentation"

## Additionnal addons
TODO

### Automatically pull Git repositories

Based on [`oca_dependencies.txt`][oca-dep]

  [oca-dep]: https://github.com/OCA/maintainer-quality-tools/blob/master/sample_files/oca_dependencies.txt
TODO

### GitHub SSH authentication
TODO

## Customize this image
TODO
