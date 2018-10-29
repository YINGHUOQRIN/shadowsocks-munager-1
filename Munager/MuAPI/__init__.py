import json
import logging
from urllib.parse import urljoin, urlencode

from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest,HTTPClient


class MuAPIError(Exception):
    pass


class User:
    def __init__(self, **entries):
        # for IDE hint
        self.id = None
        self.user_name = None
        self.passwd = None
        self.port = None
        self.method = None
        self.enable = None
        self.u = None
        self.d = None
        self.transfer_enable = None

        self.plugin = ""
        self.plugin_opts = ""
        self.__dict__.update(entries)
        if "simple_obfs_http" in self.obfs:
            self.plugin = "obfs-server"
            self.plugin_opts = "obfs=http"

        elif "simple_obfs_tls" in self.obfs:
            self.plugin = "obfs-server"
            self.plugin_opts = "obfs=tls"

    @property
    def available(self):
        return True if self.disconnect_ip == None else False


class MuAPI:
    def __init__(self, config):
        self.logger = logging.getLogger()
        self.config = config
        self.url_base = self.config.get('sspanel_url')
        self.key = self.config.get('key')
        self.node_id = self.config.get('node_id')
        self.delay_sample = self.config.get('delay_sample')
        self.client = AsyncHTTPClient()

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
        return HTTPRequest(**req_para)

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
    def get_users(self, key) -> dict:
        request = self._get_request('/mod_mu/users',{"node_id":self.node_id})
        response = yield self.client.fetch(request)
        content = response.body.decode('utf-8')
        cont_json = json.loads(content, encoding='utf-8')
        if cont_json.get('ret') != 1:
            raise MuAPIError(cont_json)
        ret = dict()
        for user in cont_json.get('data'):
            ret[user.get(key)] = User(**user)
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
    def upload_throughput(self, user_id, traffic):
        request = self._get_request(
            path='/mu/users/{id}/traffic'.format(id=user_id),
            method='POST',
            query={
                'node_id': self.node_id},
            formdata={
                'u': 0,
                'd': traffic,
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
