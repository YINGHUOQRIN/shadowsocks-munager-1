FROM ubuntu:latest as builder

LABEL maintainer="Sam <allsafe@my.com>"
LABEL V2Ray = "4.8.0"

RUN apt-get update
RUN apt-get install curl -y
RUN curl -L -o /tmp/go.sh https://install.direct/go.sh
RUN chmod +x /tmp/go.sh
RUN /tmp/go.sh

FROM python:3.6.7-alpine
# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

COPY --from=builder /usr/bin/v2ray/v2ray /usr/bin/v2ray/
COPY --from=builder /usr/bin/v2ray/v2ctl /usr/bin/v2ray/
COPY --from=builder /usr/bin/v2ray/geoip.dat /usr/bin/v2ray/
COPY --from=builder /usr/bin/v2ray/geosite.dat /usr/bin/v2ray/

LABEL v2ray_api_version="0.0.1"
RUN runDeps="git build-base linux-headers py3-cffi libffi-dev"\
&& set -ex \
&& apk add --no-cache ca-certificates \
&& apk add --no-cache --virtual .build-deps ${runDeps} \
&& mkdir /var/log/v2ray/ \
&& mkdir /etc/v2ray \
&& chmod +x /usr/bin/v2ray/v2ctl \
&& chmod +x /usr/bin/v2ray/v2ray \
&& cd /etc/ \
&& git clone -b v2ray_api https://github.com/alliswell2day/shadowsocks-munager.git \
&& cd shadowsocks-munager \
&& cp config/config_example.yml config/config.yml \
&& cp config/config.json /etc/v2ray/config.json \
&& pip3 install --no-cache-dir -r requirements.txt\
&& apk del .build-deps \
&& apk add --no-cache libstdc++

ENV PATH /usr/bin/v2ray:$PATH
VOLUME /etc/v2ray/ /etc/shadowsocks-munager/ /var/log/v2ray/
WORKDIR /etc/shadowsocks-munager
CMD sed -i "s|node_id:.*|node_id: ${node_id}|" /etc/shadowsocks-munager/config/config.yml && \
sed -i "s|sspanel_url:.*|sspanel_url: '${sspanel_url}'|" /etc/shadowsocks-munager/config/config.yml && \
sed -i "s|key:.*|key: '${key}'|" /etc/shadowsocks-munager/config/config.yml && \
sed -i "s|speedtest:.*|speedtest: ${speedtest}|" /etc/shadowsocks-munager/config/config.yml && \
sed -i "s|docker:.*|docker: ${docker}|" /etc/shadowsocks-munager/config/config.yml && \
(nohup v2ray -config=/etc/v2ray/config.json >/dev/null 2>&1 & )&& \
python3 run.py --config-file=/etc/shadowsocks-munager/config/config.yml