import django
import os
from celery import Task
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dxflearn.settings")
django.setup()
from blog import customserializers
from blog import models
from django.contrib.auth.models import User
from utils.basic_log import log_django


class ArticleOperator(Task):
    name = "blog.ArticleOperator"  # 定义task的name时指定namespace=blog
    queue = "web_task"  # 指定ArticleOperator将会被发送的队列

    def get_object(self, pk):
        return models.Article.objects.get(pk=pk)

    def get_user(self, pk):
        return User.objects.get(pk=pk)

    def run(self, method, data, user=None, pk=None, *args, **kwargs):
        if method == "POST":
            serializer = customserializers.ArticleSerializer(data=data)
            user = self.get_user(user)
            if serializer.is_valid():
                # 注意：手动将request.user与author绑定
                serializer.save(author=user)
                return "success"

        elif method == "PUT" and pk is not None:
            article = self.get_object(pk)
            serializer = customserializers.ArticleSerializer(instance=article, data=data)
            if serializer.is_valid():
                serializer.save()
                return "success"

        elif method == "PUT":
            pass

    def before_start(self, task_id, args, kwargs):
        """
        重写父类的before_start方法, 这个方法是task运行前会被调用
        :param task_id:
        :param args:
        :param kwargs:
        :return:
        """
        log_django.info("任务运行前执行, task_id:{}".format(task_id, args, kwargs))

    def on_success(self, retval, task_id, args, kwargs):
        """
        重写父类的on_success方法, 这个方法是task运行成功会被调用
        :param retval:
        :param task_id:
        :param args:
        :param kwargs:
        :return:
        """
        log_django.info("任务运行成功时执行, task_id:{}".format(task_id))

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """
        重写父类的on_retry方法, 这个方法是task运行失败并重试的时候会被调用,
        这里可以记录失败的任务的task_id和参数等
        :param exc:
        :param task_id:
        :param args:
        :param kwargs:
        :param einfo:
        :return:
        """
        log_django.error("任务运行失败重试时执行, task_id:{}, einfo:{}".format(task_id, einfo))

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        重写父类的on_failure方法, 这个方法是task运行失败的时候会被调用,
        这里可以记录失败的任务的task_id和参数等
        :param exc:
        :param task_id:
        :param args:
        :param kwargs:
        :param einfo:
        :return:
        """
        log_django.error("任务运行失败时执行, task_id:{}, einfo:{}".format(task_id, einfo))

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """
        重写父类的after_return方法, 这个方法是task运行结束的时候会被调用.
        :param status:
        :param retval:
        :param task_id:
        :param args:
        :param kwargs:
        :param einfo:
        :return:
        """
        log_django.info("任务运行结束时执行, task_id:{}".format(task_id))
