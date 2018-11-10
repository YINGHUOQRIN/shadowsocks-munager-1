import logging

from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.ioloop import IOLoop, PeriodicCallback

from Munager.MuAPI import MuAPI
from Munager.SSManager import SSManager
from Munager.V2Manager import V2Manager
from Munager.SpeedTestManager import speedtest_thread

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
        if self.node_info['sort']==0:
            self.ss_manager = SSManager(self.config)
        elif self.node_info['sort']==11:
            self.v2_manager = V2Manager(self.config)
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
    def update_ss_manager(self):
        # get from MuAPI and ss-manager
        users = yield self.mu_api.get_users('port')
        state = self.ss_manager.state
        self.logger.info('get MuAPI and ss-manager succeed, now begin to check ports.')
        #self.logger.debug('get state from ss-manager: {}.'.format(state))

        # remove port
        for port in state:
            if port not in users or not users.get(port).available:
                self.ss_manager.remove(port)
                self.logger.info('remove port: {}.'.format(port))

        # add port
        for port, user in users.items():
            user_id = user.id
            if user.available and port not in state:
                if self.ss_manager.add(
                        user_id=user_id,
                        port=user.port,
                        password=user.passwd,
                        method=user.method,
                        plugin=user.plugin,
                        plugin_opts=user.plugin_opts,
                ):
                    self.logger.info('add user at port: {}.'.format(user.port))

            if user.available and port in state:
                if user.passwd != state.get(port).get('password') or \
                                user.method != state.get(port).get('method') or \
                                user.plugin != state.get(port).get('plugin') or \
                                user.plugin_opts != state.get(port).get('plugin_opts'):
                    if self.ss_manager.remove(user.port) and self.ss_manager.add(
                            user_id=user_id,
                            port=user.port,
                            password=user.passwd,
                            method=user.method,
                            plugin=user.plugin,
                            plugin_opts=user.plugin_opts,
                    ):
                        self.logger.info('reset port {} due to method or password changed.'.format(user.port))
        # check finish
        self.logger.info('check ports finished.')

    @gen.coroutine
    def upload_ss_throughput(self):
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
        if self.node_info['sort']==0:
            PeriodicCallback(
                callback=self.update_ss_manager,
                callback_time=self._second_to_msecond(self.config.get('update_port_period', 60)),
                io_loop=self.ioloop,
            ).start()
            PeriodicCallback(
                callback=self.upload_ss_throughput,
                callback_time=self._second_to_msecond(self.config.get('upload_throughput_period', 360)),
                io_loop=self.ioloop,
            ).start()
        PeriodicCallback(
            callback=self.upload_serverload,
            callback_time=self._second_to_msecond(self.config.get("upload_serverload_period",60)),
            io_loop = self.ioloop,
        ).start()
        PeriodicCallback(
            callback_time=self._second_to_msecond(self.config.get("upload_speedtest_period",21600)),
            callback=self.upload_speedtest,
            io_loop=self.ioloop
        ).start()
        try:
            # Init task
            self.ioloop.run_sync(self.upload_serverload)
            self.ioloop.start()
        except KeyboardInterrupt:
            del self.mu_api
            if self.node_info['sort']==0:
                del self.ss_manager
            elif self.node_info['sort']==11:
                del self.v2_manager
            print('Bye~')

class Munager_test:
    def __init__(self, config):
        self.config = config

        # set logger
        self.logger = logging.getLogger()

        # mix
        self.ioloop = IOLoop.current()
        self.mu_api = MuAPI(self.config)
        print(self.mu_api.get_node_info())
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
            callback=self.upload_serverload,
            callback_time=self._second_to_msecond(self.config.get("upload_serverload_period",60)),
            io_loop = self.ioloop,
        ).start()

        try:
            # Init task
            self.ioloop.run_sync(self.upload_serverload)
            self.ioloop.start()
        except KeyboardInterrupt:
            del self.mu_api
            print('Bye~')




