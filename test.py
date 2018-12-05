import requests
import pprint
import json,os,re

r = requests.get('https://alpha2.rico93.win/mod_mu/users',params={"key":"iMw48KF4roAh",'node_id':"8"})

json_data =json.loads(r.text)['data']
pprint.pprint(json_data)

r = requests.get("https://alpha2.rico93.win/mod_mu/nodes/6/info",params={"key":"iMw48KF4roAh"})
data =json.loads(r.text)['data']
temp_server = data['server'].split(";")
server = dict(zip(["server_address",'port','AlterId','protocol','protocol_param'],temp_server[:5]))
temp_extraArgs=temp_server[5].split("|")
extraArgs = {}
for i in temp_extraArgs:
    key,value = i.split("=")
    extraArgs[key]= value
server['extraArgs']=extraArgs
data['server'] = server
pprint.pprint(data)

stats_cmd = "cd /usr/bin/v2ray && ./v2ctl api --server=127.0.0.1:%s StatsService.GetStats 'name: \"%s>>>%s>>>traffic>>>%s\" reset: %s'"
type_tag = "user"

stats_real_cmd = stats_cmd % (str(8080), type_tag, 'rico931@outlook.com', "downlink", False)
downlink_result = os.system(stats_real_cmd)
if downlink_result:
    re_result = re.findall(r"\d+", downlink_result[2])
    if not re_result:
        downlink_value = 0
    else:
        downlink_value = int(re_result[0])
    print(downlink_value)



# from Munager.Template_object import Shadowsocks
# from Munager.Loader import Loader
#
# Loader()
#
# from Munager.Template_object import Shadowsocks,Vmess
#
#
# test = Vmess()
# test.update(1111)
# test.add("123123",'eiro9adsf')
# print(json.dumps(test.toJSON()))

