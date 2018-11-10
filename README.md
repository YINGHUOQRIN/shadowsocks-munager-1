
# TODO
- [x] 基于ss-libev 适配sspanel v3 魔改版
- [x] 增加测速和负载
- [ ] 全后端转向v2ray，使用v2ray提供ss和vmess代理，用v2ray自带api统计流量
- [ ] 适配sspanel v3的v2ray后端( 不知道啥时候完成，首先感谢Jrohy的[multi-v2ray](https://github.com/Jrohy/multi-v2ray),预计将在他的基础上，来适配
- [ ] 增加进程守护。
- [ ] 跑的过程中会删掉 manager config文件的端口


# 目前缺陷

ss和目前panel下的v2ray部分未来预计都只能多用户一个配置，除了id或者密码，端口不一样，
其余加密方式都是一样的。  ss这里是ss-manager通讯接口的问题，v2ray这里是panel部分现有的暂时没有这个配置返回(php 我还不会，主要是懒）
# shadowsocks-munager

我目前在使用的是来自于NimaQU的[SS-PANEL魔改版](https://github.com/NimaQu/ss-panel-v3-mod_Uim),主要适配了他的Mod_MU API 的 shadowsocks-server，通过调用 ss-manager 控制 ss-server，支持流量统计，在线人数计算，
系统负载和测速(测速部分主要代码也是来自于NimaQU的后端的SpeedTest_thread.py)


## 部署

### 编译安装 Shadowsocks-libev

推荐使用[秋水逸冰的脚本](https://shadowsocks.be/4.html)。

~~~
wget --no-check-certificate -O shadowsocks-all.sh https://raw.githubusercontent.com/teddysun/shadowsocks_install/master/shadowsocks-all.sh
chmod +x shadowsocks-all.sh
~~~

### 运行ss-manger:

具体请看 [秋水的部分](https://teddysun.com/532.html)


~~~
wget -O /etc/init.d/shadowsocks-manager https://raw.githubusercontent.com/teddysun/shadowsocks_install/master/shadowsocks-manager
chmod 755 /etc/init.d/shadowsocks-manager
~~~

~~~
mkdir /etc/shadowsocks-manager
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

- 参数 `FAST_OPEN`，不支持 TCP fast open 的内核请去掉。
- 参数 `PLUGIN` 和 `PLUGIN_OPTS` 启用混淆，有需要请到 [simple-obfs](https://github.com/shadowsocks/simple-obfs) 编译插件。

### 安装依赖

```bash
apt-get update -y
apt-get install -y gcc redis-server python3-dev python3-pip python3-setuptools
git clone https://github.com/rico93/shadowsocks-munager.git
cd shadowsocks-munager
pip3 install -r requirements.txt
vi config/config.yml
/etc/init.d/shadowsocks-libev stop
mv /etc/init.d/shadowsocks-libev ~
/etc/init.d/shadowsocks-manager start
screen -S SS
python3 run.py
```

### 启动 ss-manager 与 Munager

运行 `python3 run.py --config-file=config/config.yml` 运行脚本，


## 已知 Bug

暂未发现。
