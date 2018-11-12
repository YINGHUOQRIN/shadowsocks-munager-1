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

## V2ray （ws）目前端口监听在本地，请使用反向代理，暴露443端口 (面板节点信息有误，懒得改php了）

目前懒得改面板，只能baypss
没有cdn的域名或者ip;端口（外部链接的);AlterId;ws;;额外参数(path=/v2ray|host=xxxx.win|port=10550(这个端口内部监听))
xxxxx.com;443;16;ws;;path=/v2ray|host=oxxxx.com|port=10550

默认自己会找caddy或者nginx反向代理. 只做了ws+tls（tls走反向代理），所以生成的
config文件没有tls设置。

# TODO
- [x] 增加测速和负载
- [x] 全后端转向v2ray，使用v2ray提供ss和vmess代理，用v2ray自带api统计流量(Jrohy的[multi-v2ray](https://github.com/Jrohy/multi-v2ray)的templ和部分代码思路)
- [ ] 增加进程守护。
### V2ray:

~~~
bash <(curl -L -s https://install.direct/go.sh)
rm /etc/v2ray/config.json #这个是老版本的，得删掉程序才能跑，我指针对4.0后的格式做了适配
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
```

### 启动程序

~~~
screen -S v2ray
python3 run.py --config-file=config/config.yml
~~~



## 已知 Bug

sspanel,切换服务器类别(v2ray to ss or ss to v2ray) 会出现
EOF occurred in violation of protocol (_ssl.c:833)， 看起来像是https验证失败，
暂时不知道啥问题造成的。但是整体正常。

