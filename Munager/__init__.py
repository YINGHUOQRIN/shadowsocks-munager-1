import logging

from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.ioloop import IOLoop, PeriodicCallback

from Munager.MuAPI import MuAPI
from Munager.V2Manager import V2Manager
from Munager.SpeedTestManager import speedtest_thread
import json
def dumper(obj):
    try:
        return obj.toJSON()
    except:
        return obj.__dict__
class Munager:
    def __init__(self, config):
        self.config = config

        # set logger
        self.logger = logging.getLogger()

        # mix
        self.ioloop = IOLoop.current()
        self.mu_api = MuAPI(self.config)
        self.node_info = self.mu_api.get_node_info()
        self.logger.info("Node infos: {}".format(self.node_info))
        self.ss_manager = V2Manager(self.config,sort=self.node_info['sort'])
        self.logger.info('Munager initializing.')
    @gen.coroutine
    def upload_serverload(self):
        # update online users count
        try:
            uptime = self._uptime()
            load = self._load()
            result = yield self.mu_api.upload_systemload(uptime,load)
            if result:
                self.logger.info('upload_system load success. uptime {}, load {}'.format(uptime,load))
        except HTTPError:
            self.logger.warning('upload_system load failed')

    @gen.coroutine
    def upload_speedtest(self):
        # update online users count
        try:
            speedtest_result = speedtest_thread()
            result = yield self.mu_api.upload_speedtest(speedtest_result)
            if result:
                self.logger.info('Successfully upload speet test result {}.'.format(speedtest_result))
        except HTTPError:
            self.logger.warning('failed to upload online user count.')
    @gen.coroutine
    def update_manager(self):
        # get from MuAPI and ss-manager
        users = yield self.mu_api.get_users('email',self.node_info['sort'])
        from Munager.Template_object import Shadowsocks,Config
        from pprint import pprint
        config = Config()
        config.updata_inboundObjects(Shadowsocks.addUsers(users.values()))
        with open("test.txt",'w',encoding='utf8') as writer:
            writer.write(str(config))
        current_user = self.ss_manager.get_users()
        self.logger.info('get MuAPI and ss-manager succeed, now begin to check ports.')
        #self.logger.debug('get state from ss-manager: {}.'.format(state))
        print(current_user.keys())
        # remove user by email
        for email in current_user:
            if email not in users or not users.get(email).available:
                self.ss_manager.remove(email)
                self.logger.info('remove client: {}.'.format(email))
        # add email
        for email, user in users.items():
            if user.available and email not in current_user:
                if self.ss_manager.add(user):
                    self.logger.info('add user email {}.'.format(user.email))

            if user.available and email in current_user:
                if user!= current_user.get(email):
                    if self.ss_manager.remove(user.email) and self.ss_manager.add(user):
                        self.logger.info('reset user {} due to method or password changed.'.format(user.email))
        print(self.ss_manager.users.keys())
        # check finish
        self.logger.info('check ports finished.')

    @gen.coroutine
    def upload_throughput(self):
        state = self.ss_manager.state
        online_amount = 0
        for port, info in state.items():
            cursor = info.get('cursor')
            throughput = info.get('throughput')
            if throughput < cursor:
                online_amount += 1
                self.logger.warning('error throughput, try fix.')
                self.ss_manager.set_cursor(port, throughput)
            elif throughput > cursor:
                online_amount += 1
                dif = throughput - cursor
                user_id = info.get('user_id')
                try:
                    result = yield self.mu_api.upload_throughput(user_id, dif)
                    if result:
                        self.ss_manager.set_cursor(port, throughput)
                        self.logger.info('update traffic: {} for port: {}.'.format(dif, port))
                except:
                    self.logger.info('update trafic faileds')


        # update online users count
        try:
            result = yield self.mu_api.post_online_user(online_amount)
            if result:
                self.logger.info('upload online user count: {}.'.format(online_amount))
        except HTTPError:
            self.logger.warning('failed to upload online user count.')

    @staticmethod
    def _second_to_msecond(period):
        # s to ms
        return period * 1000

    @staticmethod
    def _uptime():
        with open('/proc/uptime', 'r') as f:
            return float(f.readline().split()[0])

    @staticmethod
    def _load():
        import os
        return os.popen(
            "cat /proc/loadavg | awk '{ print $1\" \"$2\" \"$3 }'").readlines()[0]
    def run(self):
        # period task
        PeriodicCallback(
            callback=self.update_manager,
            callback_time=self._second_to_msecond(self.config.get('update_port_period', 60)),
            io_loop=self.ioloop,
        ).start()
        # PeriodicCallback(
        #     callback=self.upload_throughput,
        #     callback_time=self._second_to_msecond(self.config.get('upload_throughput_period', 360)),
        #     io_loop=self.ioloop,
        # ).start()
        PeriodicCallback(
            callback=self.upload_serverload,
            callback_time=self._second_to_msecond(self.config.get("upload_serverload_period",60)),
            io_loop = self.ioloop,
        ).start()
        # PeriodicCallback(
        #     callback_time=self._second_to_msecond(self.config.get("upload_speedtest_period",21600)),
        #     callback=self.upload_speedtest,
        #     io_loop=self.ioloop
        # ).start()
        try:
            # Init task
            self.ioloop.run_sync(self.update_manager)
            self.ioloop.start()
        except KeyboardInterrupt:
            del self.mu_api
            if self.node_info['sort']==0:
                del self.ss_manager
            elif self.node_info['sort']==11:
                del self.v2_manager
            print('Bye~')
