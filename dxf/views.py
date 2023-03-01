from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from utils import task


class Task(APIView):
    # @csrf_exempt 对于CBV直接使用装饰器是不行的, 需要使用装饰器method_decorator
    # 然后将csrf_exempt, csrf_protect当作参数传递进去
    @method_decorator(csrf_exempt)
    def get(self, request, *args, **kwargs):
        msg = {"name": "jiangyuxu", "age": 30}
        return Response(data=msg)

    # @csrf_protect 对于CBV直接使用装饰器是不行的, 需要使用装饰器method_decorator
    # 然后将csrf_exempt, csrf_protect当作参数传递进去
    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        print("请求post方法")
        print(1/0)
        msg = {"name": "liying", "age": 29}
        return Response(data=msg)


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
        task_instance = task.EmailTask()
        # delay_instance = task_instance.apply_async(args=(subject, message))
        task_instance.delay(subject, message)
        msg = {"msg": "邮件已经发送"}
        return Response(data=msg)

