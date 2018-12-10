import json
import logging
from urllib.parse import urljoin, urlencode
from Munager.User import SS_user,Vmess_user
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest,HTTPClient
import requests

class MuAPIError(Exception):
    pass

class MuAPI:
    def __init__(self, config):
        self.logger = logging.getLogger()
        self.config = config
        self.url_base = self.config.get('sspanel_url')
        self.key = self.config.get('key')
        self.node_id = self.config.get('node_id')
        self.client = AsyncHTTPClient()
        self.node_info = None

    def _get_request(self, path, query=dict(), method='GET', formdata=None,headers ={'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',}):
        query.update(key=self.key)
        query_s = urlencode(query)
        url = urljoin(self.url_base, path) + '?' + query_s
        req_para = dict(
            url=url,
            method=method,
            use_gzip=True,
        )
        if method == 'POST' and formdata:
            if "json" in headers["Content-Type"]:
                body = json.dumps(formdata)
            else:
                body =urlencode(formdata)
            req_para.update(
                body=body,
                headers=headers,
            )
        return HTTPRequest(connect_timeout=600, request_timeout=600,**req_para)

    @gen.coroutine
    def _make_fetch(self, _request):
        try:
            response = yield self.client.fetch(_request)
            content = response.body.decode('utf-8')
            cont_json = json.loads(content, encoding='utf-8')
            self.logger.info("{}".format(cont_json))
            if cont_json.get('ret') != 1:
                return False
            else:
                return True
        except Exception as e:
            self.logger.exception(e)
            return False

    @gen.coroutine
    def get_users(self,key,node_info) -> dict:
        sort = node_info['sort']
        if sort==0:
            current_user = SS_user
            prifix = "SS_"
        else:
            current_user = Vmess_user
            prifix = "Vmess_"
            if node_info['server']['protocol']=="tcp":
                prifix+='tcp_'
            elif node_info['server']['protocol'] == 'ws':
                if node_info['server']['protocol_param']:
                    prifix+='ws_'+node_info['server']['protocol_param']+"_"
                else:
                    prifix += 'ws_' + "none" + "_"
            elif node_info['server']['protocol']=='kcp':
                if node_info['server']['protocol_param']:
                    prifix+='kcp_'+node_info['server']['protocol_param']+"_"
                else:
                    prifix += 'kcp_' + "none" + "_"

        request = self._get_request('/mod_mu/users',{"node_id":self.node_id})
        response = yield self.client.fetch(request)
        content = response.body.decode('utf-8')
        cont_json = json.loads(content, encoding='utf-8')
        if cont_json.get('ret') != 1:
            raise MuAPIError(cont_json)
        ret = dict()
        for user in cont_json.get('data'):
            user['prefixed_id'] = prifix+user.get(key)
            user["user_id"] = user['id']
            user['id'] = user['uuid']
            ret[user['prefixed_id']] = current_user(**user)
            if 'Vmess' in prifix:
                ret[user['prefixed_id']].set_alterId(int(self.node_info['server'].get('AlterId',16)))
        return ret

    @gen.coroutine
    def post_online_user(self, amount):
        request = self._get_request(
            path='/mu/nodes/{id}/online_count'.format(id=self.node_id),
            method='POST',
            formdata={
                'count': amount,
            }
        )
        result = yield self._make_fetch(request)
        return result

    @gen.coroutine
    def upload_throughput(self, user_id, upload,donwload):
        request = self._get_request(
            path='/mu/users/{id}/traffic'.format(id=user_id),
            method='POST',
            query={
                'node_id': self.node_id},
            formdata={
                'u': upload,
                'd': donwload,
                'node_id': self.node_id
            }
        )
        result = yield self._make_fetch(request)
        return result

    @gen.coroutine
    def upload_speedtest(self,data):
        request = self._get_request(
            path='/mod_mu/func/speedtest',
            query={
                'node_id': self.node_id},
            method='POST',
            formdata={
                "data":data
            },
            headers={
                    'Content-Type': 'application/json; charset=utf-8',
                },
        )
        result = yield self._make_fetch(request)
        return result

    @gen.coroutine
    def upload_systemload(self,uptime,load):

        request = self._get_request(
            '/mod_mu/nodes/{}/info'.format(self.node_id),
            method='POST',
            formdata={
                'uptime': str(
                    uptime),
                'load': str(
                    load)}
        )
        result = yield self._make_fetch(request)
        return result

    def get_node_info(self):
        url = self.url_base+"/mod_mu/nodes/{}/info".format(self.node_id)
        r = requests.get(url, params={"key": self.key})
        data = json.loads(r.text)['data']
        temp_server = data['server'].split(";")
        server = dict(zip(["server_address", 'port', 'AlterId', 'protocol', 'protocol_param'], temp_server[:5]))
        if "protocol" in server:
            if server['protocol'] == "tls":
                server['protocol'],server['protocol_param'] = server['protocol_param'] ,server['protocol']
        temp_extraArgs = []
        if len(temp_server)==6:
            temp_extraArgs = temp_server[5].split("|")
        extraArgs = {}
        for i in temp_extraArgs:
            if i:
                key, value = i.split("=")
                extraArgs[key] = value
        server['extraArgs'] = extraArgs
        data['server'] = server
        self.node_info = data
        return data
