# 划重点
## ss

加密方式只支持：

- [] aes-256-cfb
- [] aes-128-cfb
- [] chacha20
- [] chacha20-ietf
- [] aes-256-gcm
- [] aes-128-gcm
- [] chacha20-poly1305 或称 chacha20-ietf-poly1305

## V2ray （ws）(面板节点信息有误，懒得改php了）

目前懒得改面板，只能baypss
没有cdn的域名或者ip;端口（外部链接的);AlterId;ws;;额外参数(path=/v2ray|host=xxxx.win|port=10550(这个端口内部监听))
xxxxx.com;443;16;ws;;path=/v2ray|host=oxxxx.com|port=10550

默认自己会找caddy或者nginx反向代理. 只做了ws+tls（tls走反向代理），所以生成的
config文件没有tls设置。

# TODO
- [x] 基于ss-libev 适配sspanel v3 魔改版
- [x] 增加测速和负载
- [x] 全后端转向v2ray，使用v2ray提供ss和vmess代理，用v2ray自带api统计流量
- [ ] 适配sspanel v3的v2ray后端( 不知道啥时候完成，首先感谢Jrohy的[multi-v2ray](https://github.com/Jrohy/multi-v2ray),预计将在他的基础上，来适配
- [ ] 增加进程守护。
- [ ] 跑的过程中会删掉 manager config文件的端口
### V2ray:

~~~
bash <(curl -L -s https://install.direct/go.sh)
~~~
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


### 编辑 Mu API 配置

复制 `config_example.yml` 为 `config.yml`，修改对应参数。


### 安装依赖

```bash
apt-get update -y
apt-get install -y gcc redis-server python3-dev python3-pip python3-setuptools
git clone -b v2ray https://github.com/rico93/shadowsocks-munager.git
cd shadowsocks-munager
pip3 install -r requirements.txt
screen -S v2ray
rm  /etc/v2ray/config.json
python3 run.py
```

### 启动 ss-manager 与 Munager

运行 `python3 run.py --config-file=config/config.yml` 运行脚本，


## 已知 Bug

sspanel,切换服务器类别(v2ray to ss or ss to v2ray) 会出现
EOF occurred in violation of protocol (_ssl.c:833)， 看起来像是https验证失败，
暂时不知道啥问题造成的。但是整体正常。

