# 划重点
## 目前支持 Docker-compose直接安装，推荐使用版本一
## 感谢
[ThunderingII](https://github.com/ThunderingII/v2ray_python_client) 和 [spencer404](https://github.com/spencer404/v2ray_api) 关于python 调用api 的项目和示例。

## 项目状态
g
目前适配的是[sspanel 魔改版](https://github.com/NimaQu/ss-panel-v3-mod_Uim)的webapi，

然后目前只适配了流量记录，服务器是否在线，在线人数，负载，speedtest后端测速，延迟，后端按照前端设定自动调用API增加用户。

目前ss的适配是一个用户一个端口，v2的kcp，tcp，ws都是多用户共用一个端口。

## 已知 Bug

sspanel,切换服务器类别(v2ray to ss or ss to v2ray) 会出现
EOF occurred in violation of protocol (_ssl.c:833)， 看起来像是https验证失败，
暂时不知道啥问题造成的。但是整体正常。

还有是一定偶然几率会出现，面板服务器下线(但能够正常使用），看log发现卡在测速（目前默认不测速），可以直接重启脚本就好了

## ss

面板配置是节点类型shadowsocks, 普通端口

加密方式只支持：

- [x] aes-256-cfb
- [x] aes-128-cfb
- [x] chacha20
- [x] chacha20-ietf
- [x] aes-256-gcm
- [x] aes-128-gcm
- [x] chacha20-poly1305 或称 chacha20-ietf-poly1305

## V2ray 支持kcp，ws, tls 由镜像Caddy提供

这里面板设置是节点类型v2ray, 普通端口

[面板设置说明 主要是这个](https://github.com/NimaQu/ss-panel-v3-mod_Uim/wiki/v2ray-%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B)

没有cdn的域名或者ip;端口（外部链接的);AlterId;ws;;额外参数(path=/v2ray|host=xxxx.win|inside_port=10550这个端口内部监听))

xxxxx.com;443;16;ws;;path=/v2ray|host=oxxxx.com|inside_port=10550

xxxxx.com;443;16;tls;ws;path=/v2ray|host=oxxxx.com|inside_port=10550

目前逻辑是如果为外部链接的端口是443，则默认监听本地127.0.0.1:inside_port，对外暴露443 (如果想用kcp，走443端口，建议设置流量转发)

如果外部端口设定不是443，监听0.0.0.0:外部设定端口，所有用户的单端口，此时inside_port弃用。

默认自己会找caddy或者nginx反向代理. 只做了ws+tls（tls走反向代理），所以生成的

config文件没有tls设置。

kcp支持所有v2ray的type：

- none: 默认值，不进行伪装，发送的数据是没有特征的数据包。：xxxxx.com;443;16;kcp;noop;path=/v2ray|host=oxxxx.com|inside_port=10550

- srtp: 伪装成 SRTP 数据包，会被识别为视频通话数据（如 FaceTime）。：xxxxx.com;443;16;kcp;srtp;path=/v2ray|host=oxxxx.com|inside_port=10550

- utp: 伪装成 uTP 数据包，会被识别为 BT 下载数据。xxxxx.com;443;16;kcp;utp;path=/v2ray|host=oxxxx.com|inside_port=10550

- wechat-video: 伪装成微信视频通话的数据包。：xxxxx.com;443;16;kcp;wechat-video;path=/v2ray|host=oxxxx.com|inside_port=10550
- dtls: 伪装成 DTLS 1.2 数据包。：xxxxx.com;443;16;kcp;dtls;path=/v2ray|host=oxxxx.com|inside_port=10550
- wireguard: 伪装成 WireGuard 数据包。(并不是真正的 WireGuard 协议) ： xxxxx.com;443;16;kcp;wireguard;path=/v2ray|host=oxxxx.com|inside_port=10550

# TODO
- [x] 增加测速和负载
- [x] 全后端转向v2ray，使用v2ray提供ss和vmess代理，用v2ray自带api统计流量(Jrohy的[multi-v2ray](https://github.com/Jrohy/multi-v2ray)的templ和部分代码思路)
- [x] 使用docker


### BBR :

看 [Rat的](https://www.moerats.com/archives/387/)
openzv 看这里 [南琴浪](https://github.com/tcp-nanqinlang/wiki/wiki/lkl-haproxy)


~~~
wget -N --no-check-certificate "https://raw.githubusercontent.com/chiakge/Linux-NetSpeed/master/tcp.sh" && chmod +x tcp.sh && ./tcp.sh
~~~

Ubuntu 18.04魔改BBR暂时有点问题，可使用以下命令安装：
~~~
wget -N --no-check-certificate "https://raw.githubusercontent.com/chiakge/Linux-NetSpeed/master/tcp.sh"
apt install make gcc -y
sed -i 's#/usr/bin/gcc-4.9#/usr/bin/gcc#g' '/root/tcp.sh'
chmod +x tcp.sh && ./tcp.sh
~~~

### 脚本安装

~~~
curl https://raw.githubusercontent.com/rico93/shadowsocks-munager/v2ray_api/install.sh -o install.sh
bash install.sh
~~~

####脚本说明

务必将脚本和生成的Caddyfile，docker-compose.yml 文件放在同一目录下。 并在该目录下运行脚本

- [x] 脚本适配后端，并安装docker，docker-compose，启动服务
- [x] 查看日志
- [x] 更新config
- [x] 更新images

### 安装Docker

~~~
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
~~~

### 推荐docker-compose 安装：

推荐二进制安装 ：

~~~
sudo curl -L https://github.com/docker/compose/releases/download/1.17.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
~~~


安装 docker-compose
~~~
pip install -U docker-compose
~~~

bash 补全命令
~~~
curl -L https://raw.githubusercontent.com/docker/compose/1.8.0/contrib/completion/bash/docker-compose > /etc/bash_completion.d/docker-compose
~~~

卸载

如果是二进制包方式安装的，删除二进制文件即可。
~~~
sudo rm /usr/local/bin/docker-compose
~~~
如果是通过 pip 安装的，则执行如下命令即可删除。
~~~
sudo pip uninstall docker-compose
~~~

### 版本一 Caddy提供tls(ws)

创建 Caddyfile

~~~
{$V2RAY_DOMAIN}
{
  root /srv/www
  log ./caddy.log
  proxy {$V2RAY_PATH} localhost:10550 {
    websocket
    header_upstream -Origin
  }
  gzip
  tls {$V2RAY_EMAIL} {
    protocols tls1.0 tls1.2
    # remove comment if u want to use cloudflare ddns
    # dns cloudflare
  }
}
~~~

创建 docker-compose.yml 并修改对应项

~~~
version: '2'

services:
 v2ray:
    image: rico93/v2ray_v3:api_alpine
    restart: always
    network_mode: "host"
    environment:
      sspanel_url: "https://xxxx"
      key: "xxxx"
      docker: "true"
      speedtest: "false"
      node_id: 10
    logging:
      options:
        max-size: "10m"
        max-file: "3"

 caddy:
    image: rico93/v2ray_v3:caddy
    restart: always
    environment:
      - ACME_AGREE=true
#      if u want to use cloudflare ddns service
#      - CLOUDFLARE_EMAIL=xxxxxx@out.look.com
#      - CLOUDFLARE_API_KEY=xxxxxxx
      - V2RAY_DOMAIN=xxxx.com
      - V2RAY_PATH=/v2ray
      - V2RAY_EMAIL=xxxx@outlook.com
    network_mode: "host"
    volumes:
      - ./.caddy:/root/.caddy
      - ./Caddyfile:/etc/Caddyfile
~~~

运行

~~~
docker-compose up (加上 -d 后台运行）
~~~

#### 版本二 单纯一个V2ray

创建 docker-compose.yml 并修改对应项

~~~
version: '2'

services:
 v2ray:
    image: rico93/v2ray_v3:api_alpine
    restart: always
    network_mode: "host"
    environment:
      sspanel_url: "https://xxxx"
      key: "xxxx"
      docker: "true"
      speedtest: "false"
      node_id: 10
    logging:
      options:
        max-size: "10m"
        max-file: "3"
~~~

运行

~~~
docker-compose up (加上 -d 后台运行）
~~~

### Pull the image （目前ubuntu（500M）和alpine（200M））
~~~
docker pull rico93/v2ray_v3:api_alpine

or docker pull rico93/v2ray_v3:api_ubuntu

docker run -d --network=host --name v2ray_v3_api -e node_id=1 -e key=ixidnf -e sspanel_url=https://xx -e docker=true --log-opt max-size=50m --log-opt max-file=3 --restart=always rico93/v2ray_v3:api_alpine
~~~


## 普通安装

安装v2ray
~~~
bash <(curl -L -s https://install.direct/go.sh)
~~~

安装依赖：Ubuntu
~~~
apt-get install -y gcc python3-dev python3-pip python3-setuptools git
~~~

Centos

~~~
yum install -y https://centos7.iuscommunity.org/ius-release.rpm
yum update
yum install -y git python36u python36u-libs python36u-devel python36u-pip gcc
python3.6 -V
~~~
安装项目
~~~
git clone -b v2ray_api https://github.com/rico93/shadowsocks-munager.git
cd shadowsocks-munager
cp config/config_example.yml config/config.yml
cp config/config.json /etc/v2ray/config.json
pip3 install -r requirements.txt or pip3.6 install -r requirements.txt
~~~

修改config.yml配置， docker: False, node_id 等

运行
~~~
screen -S v2ray
python3 run.py --config-file=config/config.yml or python3.6 run.py --config-file=config/config.yml
~~~


# 别的v2适配的项目

[ssrpanel](https://github.com/ssrpanel/SSRPanel),目前自带了一个v2ray的后端支持。

[sspanel 魔改版](https://github.com/NimaQu/ss-panel-v3-mod_Uim) wiki中有提及一个收费版的v2ray适配。


