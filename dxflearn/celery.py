# -*- coding: utf-8 -*-
"""
@Auth ： 江宇旭
@Email ：jiang.yuxu@mech-mind.net
@Time ： 2023/3/1 16:41
"""
import os
from celery import Celery, bootsteps
from kombu import Queue, Exchange
from kombu.common import QoS
from user import tasks as user_task
from steelplate import tasks as steel_task
from blog import tasks as blog_task


class NoChannelGlobalQoS(bootsteps.StartStopStep):
    """celery使用quorum_queue时需要设置qos_global=False"""
    requires = {'celery.worker.consumer.tasks:Tasks'}

    def start(self, c):
        qos_global = False

        c.connection.default_channel.basic_qos(
            0, c.initial_prefetch_count, qos_global,
        )

        def set_prefetch_count(prefetch_count):
            return c.task_consumer.qos(
                prefetch_count=prefetch_count,
                apply_global=qos_global,
            )
        c.qos = QoS(set_prefetch_count, c.initial_prefetch_count)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dxflearn.settings")
app = Celery("django_celery")
# 这个的namespace大写, 那就意味着在django的settings.py中有关celery的配置都要大写
app.config_from_object("django.conf:settings", namespace="CELERY")
# 使用quorum_queue时需要更改consumers的配置
app.steps['consumer'].add(NoChannelGlobalQoS)


queue = (
    Queue("dead_letter_queue", exchange=Exchange("dead_letter_exchange", type="direct"), routing_key="dead_letter",
          queue_arguments={
              'x-queue-type': 'classic',
              'x-max-length': 2000000,
              'x-overflow': 'drop-head',
          }),
    Queue("default_queue", exchange=Exchange("default_exchange", type='direct'), routing_key="default",
          durable=True, auto_delete=True,
          queue_arguments={'x-queue-type': 'classic', 'x-dead-letter-exchange': 'dead_letter_exchange',
                           'x-dead-letter-routing-key': 'dead_letter'}),
    Queue("topic_queue", exchange=Exchange("topic_exchange", type="topic"), routing_key="user.#",
          durable=True, auto_delete=True,
          queue_arguments={'x-max-priority': 10, 'x-queue-type': 'classic', 'x-max-length': 2000000,
                           'x-dead-letter-exchange': 'dead_letter_exchange',
                           'x-dead-letter-routing-key': 'dead_letter'
                           }),
    Queue("quorum_queue", exchange=Exchange("quorum_exchange", type="topic"), routing_key="blog.#",
          queue_arguments={
             'x-queue-type': 'quorum',
             # 'x-max-length': 2000000,
             # 'x-overflow': 'reject_publish',
             # 'x-delivery-limit': 2,
             # "x-queue-lead-locator": "balanced",
         }),

)
app.conf.update(CELERY_QUEUES=queue)
app.conf.task_queue_max_priority = 10  # 队列的最大优先级
app.conf.task_default_priority = 5  # 队列的默认优先级
app.conf.task_default_queue = "default_queue"
app.conf.task_default_exchange = "default_exchange"
app.conf.task_default_routing_key = "default"
app.conf.task_time_limit = 10  # 设置celery的硬超时时间
app.conf.task_soft_time_limit = 5  # 设置celery的软超时时间
# 除了按照上面的task_name一一映射exchange外, 还可以通过正则表达式进行映射，
# 以blog开头的task_name都会被发送到quorum_exchange中, 同时携带的routing_key是blog.task
# 以user开头的task_name都会被发送到topic_exchange中, 通过携带的routing_key时user.task
app.conf.task_routes = {
    'blog.*': {
        'exchange': 'quorum_exchange',
        'routing_key': 'blog.task',
        'priority': 10,
    },
    'user.*': {
        'exchange': 'topic_exchange',
        'routing_key': 'user.task',
        'priority': 10,
    },
}

# 要使 app.autodiscover_tasks() 自动加载celery任务, 需要在 Django 的每个应用程序内的单独创建
# tasks.py 模块, 并在tasks.py中中定义 Celery 任务
app.autodiscover_tasks()  # 会自动从django的INSTALLED_APPS中的应用目录下加载tasks.py
app.register_task(user_task.UserOperator())  # class base task 需要注册到celery中
app.register_task(steel_task.SteelOriginalInfoOperator())
app.register_task(blog_task.ArticleOperator())
app.register_task(blog_task.ClassBaseAdd())
