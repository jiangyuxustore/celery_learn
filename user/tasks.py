"""异步任务模块"""
from time import sleep
# import os
# import django
from django.core.mail import send_mail
from celery import shared_task, Task
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dxflearn.settings")
# django.setup()
# from django.contrib.auth.models import User


# ==============================================基于函数的异步任务==================================================
@shared_task()
def send_feedback_email_task(subject, message):
    """发送邮件给用户, 进行邮箱验证"""
    print("发送邮件给用户")
    sleep(10)
    send_mail(
        subject=subject,
        message=message,
        from_email='377832421@qq.com',
        recipient_list=['jiang.yuxu@mech-mind.net'],
        fail_silently=False
    )
    print("发送邮件成功")
    return 'success'

# ==============================================基于类的异步任务==================================================


class UserOperator(Task):
    name = "UserOperator"  # 必须要指定一个全局唯一的name属性, 不然celery启动的时候报错

    def run(self, username, password, email, random_uuid, *args, **kwargs):
        """
        必须要重写run方法, 这个是继承Task类的主体运行逻辑.
        写数据到mysql也可以用celery去操作, 原因耗时2秒的接口限制直接0.2s就完成了
        """
        print("开始插入数据到mysql")
        user = User.objects.create_user(username=username, password=password, email=email, is_active=0)
        print("数据插入到mysql成功, 用户id:{}".format(user.id))
        return 'success'

