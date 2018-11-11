import json
import os,re
class User:
    def __init__(self, **entries):
        # for IDE hint
        self.user_id = None
        self.id = None
        self.email = None
        self.password = None
        self.uuid = None
        self.port = None
        self.method = None
        self.enable = None
        self.u = None
        self.d = None
        self.transfer_enable = None
        self.protocol = None
        self.protocol_param = None
        self.obfs = None
        self.obfs_param = None
        self.disconnect_ip = None
        self.prefixed_id = None
        self.__dict__.update(entries)
        self.available = self.if_available()
        if 'passwd' in self.__dict__:
            self.password = self.passwd
            self.__dict__.pop('passwd')

    def if_available(self):
        return True if self.disconnect_ip == None else False

    def __str__(self):
        return json.dumps(self.__dict__)
    def get_throughput(self):
        stats_cmd = "cd /usr/bin/v2ray && ./v2ctl api --server=127.0.0.1:%s StatsService.GetStats 'name: \"%s>>>%s>>>traffic>>>%s\" reset: %s'"
        type_tag = "user"
        stats_real_cmd = stats_cmd % (str(8080), type_tag, self.email, "downlink", False)
        downlink_result = os.popen(stats_real_cmd).readlines()
        if downlink_result and len(downlink_result) == 5:
            re_result = re.findall(r"\d+", downlink_result[2])
            if not re_result:
                downlink_value = 0
            else:
                downlink_value = int(re_result[0])
        stats_real_cmd = stats_cmd % (str(8080), type_tag, self.email, "uplink", False)
        uplink_result = os.popen(stats_real_cmd).readlines()
        if uplink_result and len(uplink_result) == 5:
            re_result = re.findall(r"\d+", uplink_result[2])
            if not re_result:
                uplink_value = 0
            else:
                uplink_value = int(re_result[0])
        return uplink_value,downlink_value
class SS_user(User):
    def __init__(self, **entries):
        super(SS_user,self).__init__(**entries)
    def __eq__(self, other):
        return  other.password == self.password or \
        other.method == self.method or \
        other.id == self.id
    def get_InboundObject_json(self):
        pass

class Vmess_user(User):
    def __init__(self, **entries):
        super(Vmess_user,self).__init__(**entries)
    def __eq__(self, other):
        return other.id == self.id
    def set_alterId(self,alterId):
        self.alterId = alterId