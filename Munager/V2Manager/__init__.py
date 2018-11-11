import json
import logging
import os
import socket
import time

from redis import Redis
from Munager.Loader import Loader

class V2Manager:
    def __init__(self, config,node_info):
        self.config = config
        self.logger = logging.getLogger()
        self.sort = node_info['sort']
        self.node_info = node_info
        self.redis = Redis(
            host=self.config.get('redis_host', 'localhost'),
            port=self.config.get('redis_port', 6379),
            db=self.config.get('redis_db', 0),
        )
        self.loader =Loader()
        self.users= self.get_users()
        self.if_user_change = False
        self.logger.info('SSManager initializing.')

    @staticmethod
    def _to_unicode(_d):
        # change to unicode when get a hash table from redis
        ret = dict()
        for k, v in _d.items():
            ret[k.decode('utf-8')] = v.decode('utf-8')
        return ret

    @staticmethod
    def _fix_type(_d,keys=['traffic_upload', 'traffic_download','user_id']):
        # convert type when get a unicode dict from redis
        for key,value in _d.items():
            if key in keys:
                _d[key] = int(_d.get(key, 0))
        return _d

    def _get_key(self, _keys):
        keys = [self.config.get('redis_prefix', 'v2ray_mu')]
        keys.extend(_keys)
        return ':'.join(keys)


    def get_users(self) -> dict:

        return self.loader.get_users()
    def add(self, user):
        pipeline = self.redis.pipeline()
        pipeline.hset(self._get_key(['user', user.email]), 'traffic_upload', 0)
        pipeline.hset(self._get_key(['user', user.email]), 'traffic_download', 0)
        pipeline.hset(self._get_key(['user', user.email]), "user_id",user.user_id)
        pipeline.execute()
        time.sleep(5)
        self.if_user_change = True
        self.users[user.prefixed_id]=user
        return True

    def remove(self, email):
        if email in self.users:
            self.users.pop(email)
            self.if_user_change = True
            return True
        else:
            return False

    def update_config(self):
        self.loader.current_config.update_config(self.users,node_info=self.node_info)
    def set_current_traffic(self, user, upload,download):
        pipeline = self.redis.pipeline()
        pipeline.hset(self._get_key(['user', user.email]), 'traffic_upload', upload)
        pipeline.hset(self._get_key(['user', user.email]), 'traffic_download', download)
        pipeline.execute()
        time.sleep(5)
    def get_last_traffic(self,user):
        info = self.redis.hgetall(self._get_key(['user', user.email]))
        info = self._to_unicode(info)
        info = self._fix_type(info)
        return info['traffic_upload'],info['traffic_download'],info['user_id']
    def __del__(self):
        pass


