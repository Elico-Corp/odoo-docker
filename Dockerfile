FROM ubuntu:14.04
MAINTAINER Elico Corp <webmaster@elico-corp.com>

# Define build constants
ENV GIT_BRANCH=9.0 \
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
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" > \
  /etc/apt/sources.list.d/pgdg.list && \
  apt-get update && \
  apt-get -yq install \
    postgresql-client-$PG_VERSION \
    # Install dependencies as distrib packages when system bindings are
    # required. Some of them extend the basic Odoo requirements for a better
    # "apps" compatibility.
    # Most dependencies are distributed as PIP packages at the next step
    fontconfig=2.11.0-0ubuntu4.2 \
    ghostscript=9.10~dfsg-0ubuntu10.10 \
    libxext6=2:1.3.2-1ubuntu0.0.14.04.1 \
    libxrender1=1:0.9.8-1build0.14.04.1 \
    python=2.7.5-5ubuntu3 \
    python-imaging=2.3.0-1ubuntu3.4 \
    python-lasso=2.4.0-2build1 \
    python-libxslt1=1.1.28-2ubuntu0.1 \
    python-pip=1.5.4-1ubuntu4 \
    python-pychart=1.39-7build1 \
    python-zsi=2.1~a1-3build1 \
    xfonts-base=1:1.0.3 \
    xfonts-75dpi=1:1.0.3 \
    # libpq-dev is needed to install pg_config which is required by psycopg2
    libpq-dev=10.0-1.pgdg14.04+1 \
    # These libraries are needed to install the PIP modules
    libffi-dev=3.1~rc1+r3.0.13-12ubuntu0.2 \
    libldap2-dev=2.4.31-1+nmu2ubuntu8.4 \
    libsasl2-dev=2.1.25.dfsg1-17build1 \
    libssl-dev=1.0.1f-1ubuntu2.22 \
    libxml2-dev=2.9.1+dfsg1-3ubuntu4.10 \
    libxslt1-dev=1.1.28-2ubuntu0.1 \
    python-dev=2.7.5-5ubuntu3 \
    # Librairies required for LESS
    node-less=1.4.2-1 \
    nodejs=0.10.25~dfsg2-2ubuntu1 \
    npm=1.3.10~dfsg-1 \
    # This library is necessary to upgrade PIL/pillow module
    libjpeg8-dev=8c-2ubuntu8 \
    # Git is required to clone Odoo OCB project
    git=1:1.9.1-1ubuntu0.7

# Install Odoo python dependencies
ADD sources/pip-req.txt /opt/sources/pip-req.txt
RUN pip install -r /opt/sources/pip-req.txt

# Install LESS
RUN npm install -g less@2.7.2 less-plugin-clean-css@1.5.1 && \
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
RUN /bin/bash -c "mkdir -p /opt/odoo/{etc,sources/odoo,additional_addons,data,ssh}"

# Add Odoo OCB sources and remove .git folder in order to reduce image size
WORKDIR /opt/odoo/sources
RUN git clone https://github.com/OCA/OCB.git -b $GIT_BRANCH odoo && \
  rm -rf odoo/.git

ADD sources/odoo.conf /opt/odoo/etc/odoo.conf
ADD auto_addons /opt/odoo/auto_addons

User 0

# Provide read/write access to odoo group (for host user mapping). This command
# must run before creating the volumes since they become readonly until the
# container is started.
RUN chmod -R 775 /opt/odoo && chown -R odoo:odoo /opt/odoo

VOLUME [ \
  "/opt/odoo/etc", \
  "/opt/odoo/additional_addons", \
  "/opt/odoo/data", \
  "/opt/odoo/ssh", \
  "/opt/scripts" \
]

# Use README for the help & man commands
ADD README.md /usr/share/man/man.txt
# Remove anchors and links to anchors to improve readability
RUN sed -i '/^<a name=/ d' /usr/share/man/man.txt
RUN sed -i -e 's/\[\^\]\[toc\]//g' /usr/share/man/man.txt
RUN sed -i -e 's/\(\[.*\]\)(#.*)/\1/g' /usr/share/man/man.txt
# For help command, only keep the "Usage" section
RUN from=$( awk '/^## Usage/{ print NR; exit }' /usr/share/man/man.txt ) && \
  from=$(expr $from + 1) && \
  to=$( awk '/^    \$ docker-compose up/{ print NR; exit }' /usr/share/man/man.txt ) && \
  head -n $to /usr/share/man/man.txt | \
  tail -n +$from | \
  tee /usr/share/man/help.txt > /dev/null

# Use dumb-init as init system to launch the boot script
ADD https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64.deb /opt/sources/dumb-init.deb
RUN dpkg -i /opt/sources/dumb-init.deb
ADD bin/boot /usr/bin/boot
ENTRYPOINT [ "/usr/bin/dumb-init", "/usr/bin/boot" ]
CMD [ "help" ]

# Expose the odoo ports (for linked containers)
EXPOSE 8069 8072
