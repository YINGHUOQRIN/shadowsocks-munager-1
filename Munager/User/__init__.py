import json
class User:
    def __init__(self, **entries):
        # for IDE hint
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

class SS_user(User):
    def __init__(self, **entries):
        super(SS_user,self).__init__(**entries)
    def __eq__(self, other):
        return  other.password == self.password or \
        other.method == self.method or \
        other.uuid == self.uuid
    def get_InboundObject_json(self):
        pass

class Vemss_user(User):
    def __init__(self, **entries):
        super(Vemss_user,self).__init__(**entries)
    def __eq__(self, other):
        return other.uuid == self.uuid
    def set_alterId(self,alterId):
        self.alterId = alterId