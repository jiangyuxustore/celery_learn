# -*- coding: utf-8 -*-
"""
@Auth ： 江宇旭
@Email ：jiang.yuxu@mech-mind.net
@Time ： 2023/2/28 13:20
"""
from celery import Task
import random
import os
import time
from utils.pool import mysql_pool
from django.core.mail import send_mail
os.environ['DJANGO_SETTINGS_MODULE'] = 'dxflearn.settings'


class AddTask(Task):
    """
    官方文档说不会为每个请求实例化实例，而是作为全局实例在任务注册表中注册
    也就是说, 这个AddTask类只会实例化一次, 每一次请求进来将会调用一次run方法
    """
    name = "AddTask"  # 必须要指定一个全局唯一的name属性, 不然celery启动的时候报错

    def __init__(self):
        self.random_id = random.randint(1, 100)  # 在[1, 100]范围内随机生产random_id

    def run(self, x, y, table_name, *args, **kwargs):
        """必须要重写run方法, 这个是继承Task类的主体运行逻辑"""
        print('模拟io, random_id:{}'.format(self.random_id))  # 证明多次请求用的都是一个实例
        time.sleep(2)
        result = x + y
        db = mysql_pool.get_connection()
        with db.cursor() as cur:
            cur.execute("select * from steel_original_info limit 10")
            res = cur.fetchall()
            print(res)

        return result


class EmailTask(Task):
    """邮件任务"""
    name = "EmailTask"

    def run(self, subject, message, *args, **kwargs):
        print('模拟发送邮件')
        time.sleep(2)
        send_mail(
            subject=subject,
            message=message,
            from_email='377832421@qq.com',
            recipient_list=['jiang.yuxu@mech-mind.net'],
            fail_silently=False
        )
        print('邮件发送成功')
        return 'ok'
