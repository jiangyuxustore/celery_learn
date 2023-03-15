import time
import django
import os
from celery import shared_task, Task
from celery.exceptions import SoftTimeLimitExceeded, Reject
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


class ClassBaseAdd(Task):
    """
    第三种失败重试是基于类的, 只需要指定类属性就可以进行失败重试了
    这里指定了autoretry_for, max_retries, default_retry_delay
    """
    acks_late = True
    name = "blog.ClassBaseAdd"
    autoretry_for = (Exception, )
    max_retries = 2
    default_retry_delay = 5
    ignore_result = True

    def run(self, x, y, *args, **kwargs):
        try:
            print("ClassBaseAdd开始执行")
            self.update_state(state="PROGRESS", meta={'progress': "50%"})  # 通过update_state更新任务的进度
            log_django.info('origin:{}'.format(self.request.origin))
            log_django.info('retries:{}'.format(self.request.retries))
            log_django.info('expires:{}'.format(self.request.expires))
            log_django.info('hostname:{}'.format(self.request.hostname))
            log_django.info('delivery_info:{}'.format(self.request.delivery_info))
            log_django.info('开始计算整数相加任务, 当前任务执行次数:{}, 任务由:{}发送, 执行任务的node name:{}'.format(
                self.request.retries,
                self.request.origin,
                self.request.hostname
            ))
            log_django.info("rabbitmq相关的信息:{}".format(self.request.delivery_info))
            time.sleep(8)
            self.update_state(state="PROGRESS", meta={'progress': "90%"})
            time.sleep(1)
            result = x + y
            print("ClassBaseAdd执行结束")
            return result
        except SoftTimeLimitExceeded:
            print('触发软超时')
            raise Reject("task execute timeout", requeue=False)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        class base task失败的时候不会抛出异常, 所以我们可以记录一下异常
        :param exc:
        :param task_id:
        :param args:
        :param kwargs:
        :param einfo:
        :return:
        """
        log_django.error("任务运行失败时执行, task_id:{}, einfo:{}".format(task_id, einfo))


def on_failed(self, retval, task_id, args, kwargs):
    """回调函数还有一种使用方式就是注册到装饰器中"""
    print('任务执行失败了')


@shared_task(name='blog.function_base_add', bind=True, acks_late=True, on_failed=on_failed)
def function_base_add(self, x, y):
    """
    bind=True, 则第一个参数就是class base task中的self实例, 然后你在下面就可以用self.retry了
    第一种失败重试的方式是用try...exception捕获异常, 然后调用self.retry进行重试
    :param self:
    :param x:
    :param y:
    :return:
    """
    try:
        print('function_base_add开始执行')
        time.sleep(10)
        result = x + y
        print('function_base_add执行结束')
        return result
    except SoftTimeLimitExceeded:  # 当触发软超时就直接将数据发送给至死信队列中
        print('触发软超时')
        raise Reject("task execute timeout", requeue=False)


# 第二种失败重试就是在使用shared_task装饰器的时候，指定autoretry_for这个是你想重试的错误类型列表
# retry_kwargs是失败重试的配置, 这里指定了最大的重试次数是2次, 每次重试之间间隔8s
@shared_task(name='blog.function_base_add_v2', bind=True, autoretry_for=(Exception, ), retry_kwargs={"max_retry": 2, "countdown": 8})
def function_base_add_v2(self, x, y):
    print('function_base_add_v2开始执行')
    time.sleep(8)
    result = x + y
    print('function_base_add_v2执行结束')
    return result
