import time
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from dxflearn.tasks import send_feedback_email_task


class SteelPlate(APIView):
    # def get(self, request, *args, **kwargs):
    #     msg = {"name": "jiangyuxu", "age": 30}
    #     return Response(data=msg)

    def post(self, request, *args, **kwargs):
        print("请求post方法")
        msg = {"name": "liying", "age": 29, "address": "安亭"}
        return Response(data=msg)


class Email(APIView):

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

    def post(self, request, *args, **kwargs):
        subject = request.data['subject']
        message = request.data['message']
        send_feedback_email_task.delay(subject, message)
        msg = {"msg": "邮件已经发送"}
        return Response(data=msg)
