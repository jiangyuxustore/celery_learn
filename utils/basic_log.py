# -*- coding: utf-8 -*-
"""
@Auth ： 江宇旭
@Email ：jiang.yuxu@mech-mind.net
@Time ： 2022/6/13 11:02

log creator, that can create some unified log files
"""
import os
from loguru import logger


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
log_folder = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(log_folder):
    os.mkdir(log_folder)


class LogCreator(object):
    def __init__(self):
        self.log_folder = log_folder
        self.logger = logger
        self.logger.remove(handler_id=None)

    def create_log_file(self, log_name, rotation='00:00', retention='5 days'):
        """
        创建日志文件对象，并返回日志文件对象，你可以使用返回的日志文件对象进行日志的
        记录，此对象可以自动创建新的日志文件，也可以根据设置的周期时间进行垃圾清理
        :param log_name: str, 日志文件名称
        :param rotation: str, 自动创建日志文件的时间周期字符串, '00:00'
                        每天夜里12点进行新的日志文件创建
        :param retention: str, 垃圾清理周期, '5 days'表示 清理5天前的日志，
                        5天前的日志将会被自动删除
        :return:
        """
        base_sink = '%s.log' % log_name
        log_file_path = os.path.join(self.log_folder, base_sink)
        logger.add(
            sink=log_file_path,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} {level} {thread.name} "
                   "{thread.id} [{file.name}-line:{line}] : {message}",
            filter=self.make_filter(log_name),
            rotation=rotation, retention=retention
            )

        log_file_handle = self.logger.bind(name=log_name)
        return log_file_handle

    def make_filter(self, name):
        def filter(record):
            return record["extra"].get("name") == name

        return filter


_log_creator_object = LogCreator()
log_django = _log_creator_object.create_log_file('django') #adapter日志