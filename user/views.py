import datetime
import uuid
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.versioning import URLPathVersioning
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from user.customauth import Authentication, TokenAuthentication, SessionAuthentication
from user.customauth import create_token
from user.custompermissions import SuperPermission
from user.customserializer import OrderSerializer
from user.customthrottle import VisitThrottle
from rest_framework import status
from user.tasks import send_feedback_email_task, UserOperator
from user.models import Order


class Register(APIView):
    """用户注册类"""
    def get(self, request, *args, **kwargs):
        """返回用户注册页面"""
        request.session.set_test_cookie()
        return render(request, "register.html")

    def post(self, request, *args, **kwargs):
        """接收用户名密码并存储到数据库, 同时给用户发送一封邮件进行验证"""
        version = kwargs.get("version")
        if version == "v1":
            response = self.execute_v1(request, *args, **kwargs)
            return response
        elif version == "v2":
            response = self.execute_v2(request, *args, **kwargs)
            return response

    def execute_v1(self, request, *args, **kwargs):
        """v1版本的接口是先执行同步的用户数据保存, 然后执行异步的邮件发送"""
        start_time = time.time()
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        user = User.objects.create_user(username=username, password=password, email=email, is_active=0)
        end_save_time = time.time()
        print("数据插入耗时:{}".format(end_save_time - start_time))
        random_uuid = str(uuid.uuid1())
        # 这里设置session, 待会邮件验证的那个接口会需要用这个userid和random_uuid进行验证
        request.session['userid'] = user.id
        request.session['random_uuid'] = random_uuid
        send_feedback_email_task.delay(subject="注册验证", message="随机验证码:{}".format(random_uuid))
        response = redirect("/user/api/v1/email-verify")
        response.set_cookie("userid", user.id)
        end_time = time.time()
        print("发送异步邮件耗时:{}".format(end_time - end_save_time))
        return response

    def execute_v2(self, request, *args, **kwargs):
        start_time = time.time()
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        random_uuid = str(uuid.uuid1())
        user = UserOperator()
        user.apply_async(args=(request, username, password, email, random_uuid))
        end_save_time = time.time()
        print("异步数据库插入耗时:{}".format(end_save_time - start_time))
        send_feedback_email_task.delay(subject="注册验证", message="随机验证码:{}".format(random_uuid))
        end_time = time.time()
        print("发送异步邮件耗时:{}".format(end_time - end_save_time))
        response = redirect("/user/api/v1/email-verify")
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
        # 从redis的session中获取userid和random_uuid进行验证
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
    """访问所有订单的接口不但要登录而且还是超级管理员权限才能访问"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [SuperPermission]
    throttle_classes = [VisitThrottle]  # 限制该接口高峰的访问频率是10/min

    def get(self, request, *args, **kwargs):
        """超级管理员才能访问, redis用户访问不了, root用户可以访问"""
        order_queryset = Order.objects.all()
        order_serializer = OrderSerializer(order_queryset, many=True)
        return Response(order_serializer.data, status=status.HTTP_200_OK)


class OrderDetail(GenericAPIView):
    """订单明细接口, 只能访问单条订单"""
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get(self, request, *args, **kwargs):
        return render(request, "order.html")

    def post(self, request, *args, **kwargs):
        """
        创建一条新的订单
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
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

    def put(self, request, *args, **kwargs):
        """更新一条订单"""
        pass


class UserList(GenericAPIView):
    """用户列表接口, 该接口只有超级管理员权限才能访问"""
    permission_classes = [SuperPermission]

    def get(self, request, *args, **kwargs):
        version = request.version
        msg = {"msg": "当前版本:{}".format(version)}
        return Response(data=msg)


class UserInfo(GenericAPIView):
    """用户明细接口, 根据主键, 去用户表中查询主键指定的用户并返回"""
    versioning_class = URLPathVersioning   # 版本控制

    def get(self, request, *args, **kwargs):
        version = request.version
        print(version)
        msg = {"msg": "当前版本:{}".format(version)}
        # 指定app_name用于反向生成url
        url = request.versioning_scheme.reverse(viewname="user:list", request=request)
        print("反向生成用户列表URL, 地址:{}".format(url))
        return Response(data=msg)
