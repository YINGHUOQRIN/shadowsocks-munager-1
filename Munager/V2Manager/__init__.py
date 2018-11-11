import json
import logging
import os
import socket
import time

from redis import Redis
from Munager.Loader import Loader

class V2Manager:
    def __init__(self, config,sort):
        self.config = config
        self.logger = logging.getLogger()
        self.sort = sort
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
    def _fix_type(_d):
        # convert type when get a unicode dict from redis
        _d['cursor'] = int(_d.get('cursor', 0))
        return _d

    def _get_key(self, _keys):
        keys = [self.config.get('redis_prefix', 'v2ray_mu')]
        keys.extend(_keys)
        return ':'.join(keys)


    def get_users(self) -> dict:

        return self.loader.get_users()
    def add(self, user):
        pipeline = self.redis.pipeline()
        pipeline.hset(self._get_key(['user', user.prefixed_id]), 'cursor', 0)
        pipeline.hset(self._get_key(['user', user.prefixed_id]), 'user_id', user.id)
        pipeline.hset(self._get_key(['user', user.prefixed_id]), 'password', user.password)
        pipeline.hset(self._get_key(['user', user.prefixed_id]), 'method', user.method)
        pipeline.hset(self._get_key(['user',user.prefixed_id]),'uuid',user.uuid)
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

    def set_cursor(self, user, data):
        self.redis.hset(self._get_key(['user',user.email]), 'cursor', data)
    def __del__(self):
        pass

