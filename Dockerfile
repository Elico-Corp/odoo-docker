FROM ubuntu:14.04
MAINTAINER Elico Corp <webmaster@elico-corp.com>

# Define build constants
ENV ODOO_VERSION=7.0 \
  PG_VERSION=9.5 \
  BINARY_NAME=openerp-server

# Set timezone to UTC
RUN ln -sf /usr/share/zoneinfo/Etc/UTC /etc/localtime

# generate locales
RUN locale-gen en_US.UTF-8 && update-locale
RUN echo 'LANG="en_US.UTF-8"' > /etc/default/locale

# Add the PostgreSQL PGP key to verify their Debian packages.
# It should be the same key as https://www.postgresql.org/media/keys/ACCC4CF8.asc
RUN apt-key adv --keyserver keyserver.ubuntu.com \
  --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8

# Add PostgreSQL's repository. It contains the most recent stable release
# of PostgreSQL.
# Install dependencies as distrib packages when system bindings are required.
# Some of them extend the basic Odoo requirements for a better "apps"
# compatibility.
# Most dependencies are distributed as PIP packages at the next step
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" > \
  /etc/apt/sources.list.d/pgdg.list && \
  apt-get update && \
  apt-get -yq install \
    ghostscript \
    postgresql-client-$PG_VERSION \
    python \
    python-pip \
    python-imaging \
    python-pychart python-libxslt1 xfonts-base xfonts-75dpi \
    libxrender1 libxext6 fontconfig \
    python-zsi \
    python-lasso \
    libzmq3 \
    # libpq-dev is needed to install pg_config which is required by psycopg2
    libpq-dev \
    # These libraries are needed to install the pip modules
    python-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    # Librairies required for LESS
    node-less \
    nodejs \
    npm \
    # This library is necessary to upgrade PIL/pillow module
    libjpeg8-dev \
    # Git is required to clone Odoo OCB project
    git

# Install Odoo python dependencies
ADD sources/pip-req.txt /opt/sources/pip-req.txt
RUN pip install -r /opt/sources/pip-req.txt

# Install LESS
RUN npm install -g less less-plugin-clean-css && \
  ln -s /usr/bin/nodejs /usr/bin/node

# must unzip this package to make it visible as an odoo external dependency
RUN easy_install -UZ py3o.template==0.9.11
RUN easy_install -UZ py3o.types==0.1.1

# install wkhtmltopdf based on QT5
# Warning: do not use latest version (0.12.2.1) because it causes the footer
# issue (see https://github.com/odoo/odoo/issues/4806)
ADD https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.1/wkhtmltox-0.12.1_linux-trusty-amd64.deb \
  /opt/sources/wkhtmltox.deb
RUN dpkg -i /opt/sources/wkhtmltox.deb

# Startup script for custom setup
ADD sources/startup.sh /opt/scripts/startup.sh

# Create the odoo user
RUN useradd --create-home --home-dir /opt/odoo --no-log-init odoo

# Switch to user odoo to create the folders mapped with volumes, else the
# corresponding folders will be created by root on the host
USER odoo

# If the folders are created with "RUN mkdir" command, they will belong to root
# instead of odoo! Hence the "RUN /bin/bash -c" trick.
RUN /bin/bash -c "mkdir -p /opt/odoo/{bin,etc,sources/odoo,additional_addons,data,ssh}"
RUN /bin/bash -c "mkdir -p /opt/odoo/var/{run,log,egg-cache}"

# Add Odoo OCB sources and remove .git folder in order to reduce image size
WORKDIR /opt/odoo/sources
RUN git clone https://github.com/OCA/OCB.git -b $ODOO_VERSION odoo && \
  rm -rf odoo/.git

ADD sources/odoo.conf /opt/odoo/etc/odoo.conf
ADD auto_addons /opt/odoo/auto_addons

User 0

# Provide read/write access to odoo group (for host user mapping). This command
# must run before creating the volumes since they become readonly until the
# container is started.
RUN chmod -R 775 /opt/odoo && chown -R odoo:odoo /opt/odoo

VOLUME [ \
  "/opt/odoo/var", \
  "/opt/odoo/etc", \
  "/opt/odoo/additional_addons", \
  "/opt/odoo/data", \
  "/opt/odoo/ssh", \
  "/opt/scripts" \
]

# Use README for the help command and only keep the "Usage" section
ADD README.md /usr/share/man/help.txt
RUN from=$( awk '/^## Usage/{ print NR; exit }' /usr/share/man/help.txt ) && \
  to=$( awk '/^    \$ docker-compose up/{ print NR; exit }' /usr/share/man/help.txt ) && \
  head -n $to /usr/share/man/help.txt | \
  tail -n +$from | \
  tee /usr/share/man/help.txt > /dev/null

# Set the default entrypoint (non overridable) to run when starting the container
ADD bin /app/bin/
ENTRYPOINT [ "/app/bin/boot" ]
CMD [ "help" ]

# Expose the odoo ports (for linked containers)
EXPOSE 8069 8072
