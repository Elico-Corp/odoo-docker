FROM elicocorp/odoo:7.0
MAINTAINER Elico-Corp <contact@elico-corp.com>

# SM: Ubuntu CN mirror
RUN sed -i 's/archive\.ubuntu\.com/mirrors.sohu.com/g' /etc/apt/sources.list

# SM: pip CN mirror
RUN mkdir -p ~/pip && \
  echo "[global]" > ~/pip/pip.conf && \
  echo "index-url = https://pypi.mirrors.ustc.edu.cn/simple" >> ~/pip/pip.conf

# CN fonts
RUN apt-get update && \
  apt-get -y install ttf-wqy-zenhei