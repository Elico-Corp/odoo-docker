FROM ubuntu:16.04
MAINTAINER Elico Corp <webmaster@elico-corp.com>

# Define build constants
ENV GIT_BRANCH=8.0 \
  PG_VERSION=9.5 \
  BINARY_NAME=openerp-server

# Set timezone to UTC
RUN ln -sf /usr/share/zoneinfo/Etc/UTC /etc/localtime

# FIXME not working with Ubuntu 16.04
# Generate locales
RUN apt update \
  && apt -yq install locales \
  && locale-gen en_US.UTF-8 \
  && update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

RUN apt update \
  && apt -yq install \
    fontconfig=2.11.94-0ubuntu1.1 \
    git=1:2.7.4-0ubuntu1.3 \
    libffi-dev=3.2.1-4 \
    libjpeg-turbo8=1.4.2-0ubuntu3 \
    libldap2-dev=2.4.42+dfsg-2ubuntu3.2 \
    libsasl2-dev=2.1.26.dfsg1-14build1 \
    libssl-dev=1.0.2g-1ubuntu4.8 \
    libxml2-dev=2.9.3+dfsg1-1ubuntu0.3 \
    libxrender1=1:0.9.9-0ubuntu1 \
    libxslt1-dev=1.1.28-2.1ubuntu0.1 \
    node-less=1.6.3~dfsg-2 \
    nodejs=4.2.6~dfsg-1ubuntu4.1 \
    npm=3.5.2-0ubuntu4 \
    postgresql-client-$PG_VERSION \
    python-dev=2.7.11-1 \
    python-pip=8.1.1-2ubuntu0.4 \
    sudo=1.8.16-0ubuntu1.5 \
    zlib1g-dev=1:1.2.8.dfsg-2ubuntu4.1

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
RUN git clone https://github.com/OCA/OCB.git -b $GIT_BRANCH odoo \
  && rm -rf odoo/.git

ADD sources/odoo.conf /opt/odoo/etc/odoo.conf
ADD auto_addons /opt/odoo/auto_addons

User 0

# Install Odoo python dependencies
RUN pip install -r /opt/odoo/sources/odoo/requirements.txt

# Install extra python dependencies
ADD sources/requirements.txt /opt/sources/requirements.txt
RUN pip install -r /opt/sources/requirements.txt

# Install LESS
RUN npm install -g less@2.7.3 less-plugin-clean-css@1.5.1 \
  && ln -s /usr/bin/nodejs /usr/bin/node

# Install wkhtmltopdf based on QT5
# Warning: do not use latest version (0.12.2.1) because it causes the footer
# issue (see https://github.com/odoo/odoo/issues/4806)
ADD https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.1/wkhtmltox-0.12.1_linux-trusty-amd64.deb \
  /opt/sources/wkhtmltox.deb
RUN dpkg -i /opt/sources/wkhtmltox.deb

# Startup script for custom setup
ADD sources/startup.sh /opt/scripts/startup.sh

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

