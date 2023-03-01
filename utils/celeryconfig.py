# -*- coding: utf-8 -*-
"""
@Auth ： 江宇旭
@Email ：jiang.yuxu@mech-mind.net
@Time ： 2023/2/28 13:18
"""


broker_url = 'pyamqp://liying:jiangyuxu@124.70.136.165:5672'
result_backend = 'redis://:django-insecure-jiangyuxu-learn-django@124.70.136.165:6379/1'

accept_content = ['json']
result_accept_content = ['json']
enable_utc = True
timezone = 'Asia/Shanghai'


worker_concurrency = 1  # worker个数, 默认等于CPU个数


# Task result backend settings
result_expires = 3600  # 设置存在redis中的结果3600秒后过期
