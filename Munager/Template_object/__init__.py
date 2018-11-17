import json
class InboundObject:
    def __init__(self):
        self.port = None
        self.listen = None
        self.protocol = None
        self.settings = {}
        self.streamSettings = {}
        with open("json_template/InboundObject.json", 'r') as reader:
            data = json.load(reader)
        self.__dict__.update(data)

    def __str__(self):
        return json.dumps(self.__dict__)
    def toJSON(self):
        return self.__dict__
    def update(self,**kwargs):
        pass

    @staticmethod
    def addUsers(users,node_info=None):
        pass
class Shadowsocks(InboundObject):
    def __init__(self):
        super(Shadowsocks,self).__init__()
        with open("json_template/ss.json",'r') as reader:
            data = json.load(reader)
        self.settings = data
        self.protocol = "shadowsocks"
        self.listen = "0.0.0.0"
    def update(self,email=None,method=None,password=None,port=None):
        if port:
            self.port = port
        if email:
            self.settings['email']=email
        if method:
            self.settings['method'] = method
        if password:
            self.settings['password'] = password
    @staticmethod
    def addUsers(users,node_info=None):
        result =[]
        for user in users:
            ss = Shadowsocks()
            ss.update(email=user.email,method=user.method,password=user.password,port=user.port)
            result.append(ss.toJSON())
        return result


class Vmess(InboundObject):
    def __init__(self,alterId=16):
        super(Vmess,self).__init__()
        self.protocol = "vmess"
        self.alterId = alterId
        self.current_id = set()

    def set_alterId(self,alterId):
        self.alterId = alterId

    def load_Template(self,name):
        with open("json_template/{}.json".format(name),'r') as reader:
            data = json.load(reader)
        return data

    def update_port(self,port=None):
        if port:
            self.port = port

    def set_ws_head_path(self,extraArgs=None):
        if extraArgs:
            self.streamSettings['wsSettings']['path'] = extraArgs.get("path","")
            self.streamSettings['wsSettings']['headers']["Host"] = extraArgs.get("host","")
    def add(self,id=None,email=None):
        if id not in self.current_id:
            clientobject= self.load_Template("ClineObject")
            clientobject['id'] = id
            clientobject['alterId'] =self.alterId
            clientobject['email'] = email
            if 'clients' in self.settings:
                self.settings['clients'].append(clientobject)
            else:
                self.settings['clients'] = [clientobject]
            self.current_id.add(id)
    @staticmethod
    def addUsers(users,node_info=None):

        extraArgs = node_info['server'].get('extraArgs', {})
        vmess = Vmess(int(node_info['server'].get("AlterId","16")))
        if node_info['server'].get('port', "443")=="443":
            # 判断是否是443端口（默认这个给caddy或者nginx了),
            vmess.update_port(int(extraArgs.get("port","10550")))
            vmess.listen = "127.0.0.1"
        else:
            #如果不是443 默认不使用caddy，nginx的话，直接暴露端口给外部
            vmess.update_port(int(node_info['server'].get('port', "443")))
        if node_info['server'].get('protocol',"") == 'ws':
            vmess.streamSettings = vmess.load_Template("ws")
            vmess.set_ws_head_path(extraArgs)

        if node_info['server'].get('protocol',"") == 'tcp':
            vmess.streamSettings = vmess.load_Template("tcp")
        if node_info['server'].get('protocol',"") == 'kcp':
            vmess.streamSettings = vmess.load_Template("kcp")
            if node_info['server']['protocol_param']:
                vmess.streamSettings['kcpSettings']['header']['type'] = node_info['server']['protocol_param']
            else:
                vmess.streamSettings['kcpSettings']['header']['type'] = 'none'
        for user in users:
            vmess.add(id=user.id,email=user.email)
        return [vmess.toJSON()]

    def __str__(self):
        return json.dumps({ key:value for key,value in self.__dict__.items() if key !='current_id'})
    def toJSON(self):
        return {key:value for key,value in self.__dict__.items()if key !='current_id'}





class Config:
    def __init__(self,path="json_template/config.json"):
        with open(path,'r') as reader:
            data = json.load(reader)
        self.__dict__.update(data)


    def __str__(self):
        return json.dumps(self.__dict__,indent=4,sort_keys=True)
    def load_stat_inbound(self):
        with open("json_template/stat_inbound.json") as reader:
            data = json.load(reader)
        return data
    def update_config(self,users,node_info=None):
        ss = []
        vmess = []
        for key in users:
            if "SS_" in key:
                ss.append(users[key])
            if "Vmess_" in key:
                vmess.append(users[key])
        self.inbounds = [self.load_stat_inbound()]
        if ss:
            inboundObjects =Shadowsocks.addUsers(ss)
            self.inbounds.extend(inboundObjects)
        if vmess:
            inboundObjects = Vmess.addUsers(vmess,node_info=node_info)
            self.inbounds.extend(inboundObjects)





