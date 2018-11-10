import json
import logging
import os
import socket
import time

from redis import Redis


class V2Manager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger()
        self.redis = Redis(
            host=self.config.get('redis_host', 'localhost'),
            port=self.config.get('redis_port', 6379),
            db=self.config.get('redis_db', 0),
        )

        # load throughput log to redis
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
        keys = [self.config.get('redis_prefix', 'mu')]
        keys.extend(_keys)
        return ':'.join(keys)

    @property
    def state(self) -> dict:
        #统计流量
        pass

    def add(self, user_id, port, password, method, plugin, plugin_opts):
        msg = dict(
            server_port=port,
            password=password,
            method=method,
            fast_open=self.config.get('fast_open'),
            mode=self.config.get('mode'),
            plugin=plugin,
            plugin_opts=plugin_opts,
        )
        # to bytes
        pipeline = self.redis.pipeline()
        pipeline.hset(self._get_key(['user', str(port)]), 'cursor', 0)
        pipeline.hset(self._get_key(['user', str(port)]), 'user_id', user_id)
        pipeline.hset(self._get_key(['user', str(port)]), 'password', password)
        pipeline.hset(self._get_key(['user', str(port)]), 'method', method)
        pipeline.hset(self._get_key(['user', str(port)]), 'plugin', plugin)
        pipeline.hset(self._get_key(['user', str(port)]), 'plugin_opts', plugin_opts)
        pipeline.execute()
        time.sleep(5)
        return True

    def remove(self, port):
        #删除用户
        pass
    def set_cursor(self, port, data):
        #写入流量
        self.redis.hset(self._get_key(['user', str(port)]), 'cursor', data)
