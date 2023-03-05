import time
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail

from rest_framework.generics import GenericAPIView
from dxf import models


class Email(APIView):
    """同步发送email, 这个会post请求会一直堵塞直到email发送成功"""
    def post(self, request, *args, **kwargs):
        subject = request.data['subject']
        message = request.data['message']
        time.sleep(3)
        send_mail(
            subject=subject,
            message=message,
            from_email='377832421@qq.com',
            recipient_list=['jiang.yuxu@mech-mind.net'],
            fail_silently=False
        )
        msg = {"msg": "邮件已经发送"}
        return Response(data=msg)


class AsyncEmail(APIView):
    """这个是异步发送email, 这个post请求会直接返回, 发送邮件的过程通过celery去执行"""
    def post(self, request, *args, **kwargs):
        subject = request.data['subject']
        message = request.data['message']
        send_feedback_email_task.delay(subject, message)
        msg = {"msg": "邮件已经发送"}
        return Response(data=msg)


class OrderListV1(APIView):
    """
    访问OrderListV1必须要先登录
    OrderListV1类提供2个方法, 一个是返回所有订单, 一个是创建新的订单.
    返回所有订单的接口要根据用户的类型进行区别, 如果是超级用户则返回所有用户的所有订单
                                        如果是普通用户则值返回该用户的所有订单
    """
    def get(self, request, *args, **kwargs):
        is_super = request.user.is_super
        if is_super:
            order_list = models.Order.objects.all()
        else:
            order_list = models.Order.objects.filter(user=request.user)
        return Response(data=order_list)

    def post(self, request, *args, **kwargs):
        pass


# class OrderListV2(GenericAPIView):
#     queryset = models.Order.objects.all()
#     serializer_class = []

