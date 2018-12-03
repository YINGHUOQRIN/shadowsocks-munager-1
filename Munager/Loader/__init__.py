import os,json
from Munager.User import SS_user,Vmess_user
from Munager.Template_object import Config,Shadowsocks
import logging
class Loader:
    def __init__(self, path='/etc/v2ray/config.json'):
        self.path = path
        self.modify_time =None
        if os.path.exists(path):
            self.modify_time = os.path.getmtime(path)
        self.current_config = self.read_json()
        self.users = self.init_users()

        self.logger = logging.getLogger()
    def read_json(self):
        if os.path.exists(self.path):
            return Config(self.path)
        else:
            return Config()
    def init_users(self):
        users = {}
        for i in self.current_config.inbounds:
            if i['protocol']=="shadowsocks":
                settings = i['settings']
                settings['port'] = i['port']
                users['SS_'+settings['email']]= SS_user(**settings)

            if i['protocol']=="vmess":
                clients = i['settings']["clients"]
                prefixid = "Vmess_"
                networksetting = i['streamSettings']['network']
                if networksetting == 'tcp':
                    prefixid+="tcp_"
                elif networksetting == "kcp":
                    prefixid+="kcp_"+i['streamSettings']['kcpSettings']['header']['type']+"_"
                for client in clients:
                    users[prefixid+client['email']]= Vmess_user(**client)
        return users
    def get_users(self):
        if os.path.exists(self.path):
            if self.modify_time != os.path.getatime(self.path):
                #update_config
                self.current_config = self.read_json()
        self.users = self.init_users()
        return self.users
    def __str__(self):
        return json.dumps(self.current_config)

    def write(self):
        self.logger.info("Writing new config.json")
        with open(self.path,'w',encoding='utf8') as writer:
            writer.write(str(self.current_config))
    def restart(self):
        self.logger.info("Restart V2ray Service")
        service_name = ["v2ray", "nginx", "httpd", "apache2"]
        start_cmd = "/etc/init.d/{} start >/dev/null 2>&1"
        stop_cmd = "/etc/init.d/ {} stop >/dev/null 2>&1"
        status_cmd ="/etc/init.d/{} status >/dev/null 2>&1"
        os.system(stop_cmd.format("v2ray"))
        os.system(start_cmd.format("v2ray"))

        result = os.system(status_cmd.format('v2ray'))
        if result!=768:
            self.logger.info("v2ray running !!!")
        else:
            self.logger.warn("There is something wrong, v2ray didn't run service")

