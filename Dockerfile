FROM ubuntu:16.04 as builder
LABEL maintainer="Rico <rico93@outlook.com>"
RUN apt-get update \
    && apt-get install curl -y \
    && curl -L -o /tmp/go.sh https://install.direct/go.sh \
    && chmod +x /tmp/go.sh \
    && /tmp/go.sh \
    && rm /etc/v2ray/config.json

RUN runDeps="gcc redis-server python3-dev python3-pip python3-setuptools git"\
	&& set -ex \
	&& apt-get install -y ${runDeps} \
	&& cd /etc/ \
	&& git clone -b v2ray_docker https://github.com/rico93/shadowsocks-munager.git \
    && cd shadowsocks-munager \
    && cp config/config_example.yml config/config.yml \
    && pip3 install -r requirements.txt\
    && chmod +x /usr/bin/v2ray/v2ctl \
    && chmod +x /usr/bin/v2ray/v2ray \
    && cp config/v2ray /etc/init.d/v2ray \
    && chmod +x /etc/init.d/v2ray


ENV PATH /usr/bin/v2ray:$PATH
VOLUME /etc/v2ray/ /etc/shadowsocks-munager/ /var/log/v2ray/
WORKDIR /etc/shadowsocks-munager
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
CMD sed -i "s|node_id:.*|node_id: ${node_id}|"  /etc/shadowsocks-munager/config/config.yml && \
    sed -i "s|sspanel_url:.*|sspanel_url: '${sspanel_url}'|"  /etc/shadowsocks-munager/config/config.yml && \
    sed -i "s|key:.*|key: '${key}'|"  /etc/shadowsocks-munager/config/config.yml && \
    sed -i "s|speedtest:.*|speedtest: ${speedtest}|"  /etc/shadowsocks-munager/config/config.yml && \
    python3 run.py --config-file=/etc/shadowsocks-munager/config/config.yml