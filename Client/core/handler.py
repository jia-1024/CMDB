# -*- coding:utf-8 -*-
from core import info_collection
import json
import urllib.parse
import urllib.request
from conf import settings
import time


class ArgvHandler(object):

    def __init__(self, args):
        self.args = args
        self.parse_args()

    def parse_args(self):
        if len(self.args) > 1 and hasattr(self, self.args[1]):
            func = getattr(self, self.args[1])
            func()
        else:
            self.help_msg()

    @staticmethod
    def help_msg():
        """
        帮助说明
        :return:
        """
        msg = '''
                参数名               功能

                collect_data        测试收集硬件信息的功能

                report_data         收集硬件信息并汇报
                '''
        print(msg)

    @staticmethod
    def collect_data():
        """用于测试收集硬件信息"""
        info = info_collection.InfoCollection()
        asset_data = info.collect()
        print(asset_data)

    @staticmethod
    def report_data():
        """用于报告硬件信息"""

        info = info_collection.InfoCollection()
        asset_data = info.collect()
        data = {'asset_data': json.dumps(asset_data)}
        url = 'http://{}:{}{}'.format(settings.Params['server'], settings.Params['port'], settings.Params['url'])
        print('正在发送数据至地址：  {}'.format(url))
        try:
            data_encode = urllib.parse.urlencode(data).encode()
            response = urllib.request.urlopen(url=url, data=data_encode,
                                              timeout=int(settings.Params['request_timeout']))
            print("\033[31;7m发送完毕！\033[0m ")
            message = response.read().decode()
            print('返回结果：{}'.format(message))
        except Exception as e:
            message = '发送失败。 错误原因：   {}'.format(e)
            print("\033[31;0m{}\033[0m ".format(message))

        with open(settings.PATH, 'ab') as f:
            log = '发送时间：{} \t 服务器地址：{} \t 返回结果：{} \n '.format(time.strftime('%Y-%m-%d %H:%M:%S'), url, message)
            f.write(log.encode())
            print('日志记录成功')


