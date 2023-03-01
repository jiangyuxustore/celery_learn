# -*- coding: utf-8 -*-
"""
@Auth ： 江宇旭
@Email ：jiang.yuxu@mech-mind.net
@Time ： 2023/3/1 16:41
"""
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dxflearn.settings")
app = Celery("django_celery")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
