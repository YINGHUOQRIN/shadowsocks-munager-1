import os,json
from Munager.User import SS_user,Vemss_user
from Munager.Template_object import Config,Shadowsocks
class Loader:
    def __init__(self, path='/etc/v2ray/config.json'):
        self.path = path
        self.modify_time = os.path.getmtime(path)
        self.current_config=self.read_json()
        self.users = self.init_users()

    def read_json(self):
        if os.path.isfile(self.path):
            return Config(self.path)
        else:
            return Config()
    def init_users(self):
        users = {}
        for i in self.current_config.inbounds:
            if i['protocol']=="shadowsocks":
                settings = i['settings']
                users['SS_'+settings['email']]= SS_user(**settings)
            if i['protocol']=="vmess":
                clients = i['settings']["clients"]
                for client in clients:
                    users['Vemss_'+client['email']]= SS_user(**client)
        return users
    def get_users(self):
        if self.modify_time != os.path.getatime(self.path):
            #update_config
            self.current_config = self.read_json()
            self.users = self.init_users()
        return self.users
    def __str__(self):
        return json.dumps(self.current_config)

    def write(self):
        with open('test.json','w',encoding='uft8') as writer:
            inbounds = []
            for user,user_object in self.users.items():
                pass
