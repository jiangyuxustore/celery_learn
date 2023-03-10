"""celery异步任务必须定义在每个app的tasks.py中, 然后celery会自动加载每个app中的tasks.py"""
import django
import os
django.setup()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dxflearn.settings")
from steelplate.customserializer import SteelOriginalInfoSerializer
from celery import Task
from steelplate.models import SteelOriginalInfo


class SteelOriginalInfoOperator(Task):

    name = "SteelOriginalInfoOperator"

    def run(self, method, data, *args, **kwargs):
        if method == "POST":
            print("开始执行序列化")
            serializer_instance = SteelOriginalInfoSerializer(data=data)
            serializer_instance.is_valid()
            serializer_instance.save()
        elif method == "PUT":
            pass

        elif method == "DELETE":
            pass

