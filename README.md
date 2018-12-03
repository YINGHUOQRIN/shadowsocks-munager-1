# 重点 不适应大机场诉求，不适应大机场诉求，不适应大机场诉求

# 别的v2适配的项目

[ssrpanel](https://github.com/ssrpanel/SSRPanel),目前自带了一个v2ray的后端支持。

[sspanel 魔改版](https://github.com/NimaQu/ss-panel-v3-mod_Uim) wiki中有提及一个收费版的v2ray适配。

# 划重点

目前适配的是[sspanel 魔改版](https://github.com/NimaQu/ss-panel-v3-mod_Uim)的webapi，

然后目前只适配了流量记录，服务器是否在线，在线人数，负载，speedtest后端测速，延迟，后端按照前端设定自动修改配置文件，重启v2服务来达到的。所以不适应大机场，用户经常变动
会造成大量的v2重启服务，造成断流。

目前ss的适配是一个用户一个端口，v2的kcp，tcp，ws都是多用户共用一个端口。

## 已知 Bug

sspanel,切换服务器类别(v2ray to ss or ss to v2ray) 会出现
EOF occurred in violation of protocol (_ssl.c:833)， 看起来像是https验证失败，
暂时不知道啥问题造成的。但是整体正常。

还有是一定偶然几率会出现，面板服务器下线(但能够正常使用），看log发现卡在测速，可以直接重启脚本就好了




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

## V2ray 支持kcp，ws，（tls请用nginx或者caddy提供)，tcp 

这里面板设置是节点类型v2ray, 普通端口
目前懒得改面板，只能baypss

没有cdn的域名或者ip;端口（外部链接的);AlterId;ws;;额外参数(path=/v2ray|host=xxxx.win|inside_port=10550(这个端口内部监听))
xxxxx.com;443;16;ws;;path=/v2ray|host=oxxxx.com|port=10550

目前逻辑是如果为外部链接的端口是443，则默认监听本地127.0.0.1:inside_port，对外暴露443 (如果想用kcp，走443端口，建议设置流量转发)

如果外部端口设定不是443，监听0.0.0.0:外部设定端口，所有用户的单端口，此时inside_port弃用。

默认自己会找caddy或者nginx反向代理. 只做了ws+tls（tls走反向代理），所以生成的

config文件没有tls设置。

kcp支持所有v2ray的type：

- none: 默认值，不进行伪装，发送的数据是没有特征的数据包。：xxxxx.com;443;16;kcp;;path=/v2ray|host=oxxxx.com|inside_port=10550

- srtp: 伪装成 SRTP 数据包，会被识别为视频通话数据（如 FaceTime）。：xxxxx.com;443;16;kcp;srtp;path=/v2ray|host=oxxxx.com|inside_port=10550

- utp: 伪装成 uTP 数据包，会被识别为 BT 下载数据。xxxxx.com;443;16;kcp;utp;path=/v2ray|host=oxxxx.com|inside_port=10550

- wechat-video: 伪装成微信视频通话的数据包。：xxxxx.com;443;16;kcp;wechat-video;path=/v2ray|host=oxxxx.com|inside_port=10550
- dtls: 伪装成 DTLS 1.2 数据包。：xxxxx.com;443;16;kcp;dtls;path=/v2ray|host=oxxxx.com|inside_port=10550
- wireguard: 伪装成 WireGuard 数据包。(并不是真正的 WireGuard 协议) ： xxxxx.com;443;16;kcp;wireguard;path=/v2ray|host=oxxxx.com|inside_port=10550

# TODO
- [x] 增加测速和负载
- [x] 全后端转向v2ray，使用v2ray提供ss和vmess代理，用v2ray自带api统计流量(Jrohy的[multi-v2ray](https://github.com/Jrohy/multi-v2ray)的templ和部分代码思路)
- [ ] 增加进程守护。

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


### 安装Docker

请根据官网来

### Pull the image
$ docker pull rico93/v2ray_v3

$ docker run -d -network=host --name v2ray_v3 -e node_id=1 -e key=ixidnf -e sspanel_url=https://xx  --log-opt max-size=50m --log-opt max-file=3 --restart=always rico93/v2ray_v3