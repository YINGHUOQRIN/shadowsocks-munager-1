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
    def addUsers(users):
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
    def addUsers(users):
        result =[]
        for user in users:
            ss = Shadowsocks()
            ss.update(email=user.email,method=user.method,password=user.password,port=user.port)
            result.append(ss.toJSON())
        return result


class Vemss(InboundObject):
    def __init__(self,alterId=16):
        super(Vemss,self).__init__()
        self.protocol = "vmess"
        self.alterId = alterId
        self.current_uuid = {}
    def load_Ws_StreamSettingsObject_Template(self):
        with open("json_template/ws.json",'r') as reader:
            data = json.load(reader)
        self.streamSettings = data
    def load_ClientObject_Template(self):
        with open("json_template/ClineObject.json",'r') as reader:
            data = json.load(reader)
        return data
    def update(self,port=None):
        if port:
            self.port = port
    def add(self,uuid=None,email=None):
        if uuid not in self.current_uuid:
            clientobject= self.load_ClientObject_Template()
            clientobject['uuid'] = uuid
            clientobject['alterId'] =self.alterId
            clientobject['email'] = email
            if 'clients' in self.settings:
                self.settings['clients'].append(clientobject)
            else:
                self.settings['clients'] = [clientobject]





class Config:
    def __init__(self,path="json_template/config.json"):
        with open(path,'r') as reader:
            data = json.load(reader)
        self.__dict__.update(data)

    def __str__(self):
        return json.dumps(self.__dict__,indent=4,sort_keys=True)

    def updata_inboundObjects(self,inboundObjects):
        self.inbounds.extend(inboundObjects)




