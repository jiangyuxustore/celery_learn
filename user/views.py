import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from user.customauth import Authentication, TokenAuthentication
from user.customauth import create_token
from rest_framework import status
from user.tasks import send_feedback_email_task
from user.models import Order
import uuid


class Register(APIView):
    """用户注册类"""
    def get(self, request, *args, **kwargs):
        """返回用户注册页面"""
        request.session.set_test_cookie()
        return render(request, "register.html")

    def post(self, request, *args, **kwargs):
        """接收用户名密码并存储到数据库, 同时给用户发送一封邮件进行验证"""
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        user = User.objects.create_user(username=username, password=password, email=email, is_active=0)
        random_uuid = str(uuid.uuid1())
        print("random_uuid:{}".format(random_uuid))
        request.session['userid'] = user.id  # 设置session
        request.session['random_uuid'] = random_uuid  # 设置session
        send_feedback_email_task(subject="注册验证", message="随机验证码:{}".format(random_uuid))
        response = redirect("/user/api/v1/email-verify")
        response.set_cookie("userid", user.id)
        return response


class EmailVerify(APIView):
    """用户注册的邮件验证"""
    def get(self, request, *args, **kwargs):
        """返回邮件验证页面"""
        return render(request, "email-verify.html")

    def post(self, request, *args, **kwargs):
        """随机uuid的验证, 如果验证通过则将用户表中的is_active激活"""
        user_random_uuid = request.data.get("random_uuid")
        user_userid = int(request.COOKIES.get("userid"))
        random_uuid = request.session['random_uuid']
        userid = request.session['userid']
        msg = {"msg": "注册失败"}
        if user_userid == userid and user_random_uuid == random_uuid:
            user = User.objects.get(id=userid)
            user.is_active = 1
            user.save()
            msg = {"msg": "注册成功"}
        response = Response(msg)
        return response


class Login(APIView):
    authentication_classes = [Authentication]

    def get(self, request, *args, **kwargs):
        return render(request, "login.html")

    def post(self, request, *args, **kwargs):
        """用户名密码认证通过后, 生成一个token, 后面需要登录后才能访问的接口直接用token认证"""
        userid = request.user.id
        username = request.user.username
        is_superuser = request.user.is_superuser
        token = create_token(userid, username, is_superuser)
        data = {"msg": "登录成功"}
        response = Response(data, status.HTTP_200_OK)
        response.set_cookie("token", token)
        return response


class OrderList(APIView):
    """这里使用TokenAuthentication"""
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        user = Order.objects.filter(username=1)

    def post(self, request, *args, **kwargs):
        user = request.user
        order_id = request.data.get("order_id")
        order_amount = request.data.get("order_amount")
        order_status = request.data.get("order_status")
        order = Order(
            order_id=order_id,
            order_amount=order_amount,
            order_user=user,
            order_status=order_status
        )
        order.save()
        msg = {
            "order_id": order_id,
            "order_amount": order_amount,
            "order_user": user,
            "order_status": order_status
        }
        return Response(data=msg, status=status.HTTP_201_CREATED)


class OrderDetail(GenericAPIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        return render(request, "order.html")

    def post(self, request, *args, **kwargs):
        user = request.user
        order_id = request.data.get("order_id")
        order_amount = request.data.get("order_amount")
        order_status = request.data.get("order_status")
        order = Order(
            order_id=order_id,
            order_amount=order_amount,
            order_user=user,
            order_status=order_status,
            create_time=str(datetime.datetime.now())
        )
        order.save()
        msg = {
            "order_id": order_id,
            "order_amount": order_amount,
            "order_user": user.id,
            "order_status": order_status
        }
        return Response(data=msg, status=status.HTTP_201_CREATED)
