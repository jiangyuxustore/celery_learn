"""用户自定义认证类模块."""
from rest_framework.authentication import BaseAuthentication
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.auth import authenticate
from rest_framework import exceptions
import jwt
import time


SALT = "asgfdgerher"  # 用于jwt生成token的加盐
JWT_TOKEN_EXPIRE_TIME = 3600 * 24 * 14  # token有效期14天


def create_token(userid, username, is_superuser):
    """
    生成token
    :param userid: 用户id, 主键
    :param username: 用户名
    :param is_superuser: 用户组, 1表示超级用户
    :return:
    """
    payload = {
        "userid": userid,
        "username": username,
        "is_superuser": is_superuser,
        "exp": int(time.time()) + JWT_TOKEN_EXPIRE_TIME  # 设置token的过期时间
    }
    token = jwt.encode(payload=payload, key=SALT, algorithm='HS256')
    return token


class Authentication(BaseAuthentication):
    """
    这个类模拟实现BasicAuthentication的功能, 校验用户输入的账号和密码是否正确
    如果账号密码正确, 则生成一个token, 这样下次验证的时候就用token进行验证就不需要去数据库中查数据了减轻服务器压力
    """
    def authenticate(self, request):
        if request.method == "GET":
            return AnonymousUser(), None
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            raise exceptions.AuthenticationFailed("认证失败")
        return user, None

    def authenticate_header(self, request):
        """就算不覆盖也要重写该方法, 不然会报错"""
        pass


class TokenAuthentication(BaseAuthentication):
    """
    用户账号密码验证成功后, 生成了一个token, 其他需要用户登录才能访问的页面直接使用token认证
    这样有助于减轻数据库的压力，提升效率
    """
    def authenticate(self, request):
        token = request.COOKIES.get("token")
        user = self.verify_jwt_token(token)
        return user, None

    def authenticate_header(self, request):
        """就算不覆盖也要重写该方法, 不然会报错"""
        pass

    def verify_jwt_token(self, token):
        """
        token认证, 这里不需要再进行数据库的校验了, 直接通过jwt的token认证即可, 减少数据库的访问有助于减轻服务器压力
        token认证通过后就返回一个User instance, 因为后续的Order表有一个外键, 必须要传一个User实例
        :param token:
        :return:
        """
        payload = jwt.decode(token, SALT, algorithms=["HS256"])
        exp = int(payload['exp'])
        userid = payload["userid"]
        username = payload["username"]
        is_superuser = int(payload["is_superuser"])

        if time.time() > exp:
            raise exceptions.AuthenticationFailed("认证失效, 请重新登录")
        user = User(username=username, is_superuser=is_superuser)
        user.id = userid
        return user


class SessionAuthentication(BaseAuthentication):
    """session认证, 如果token过期了, 则使用session认证"""
    def authenticate(self, request):
        userid = request.session['userid']
        user = User()
        user.id = userid
        return User, None

    def authenticate_header(self, request):
        """就算不覆盖也要重写该方法, 不然会报错"""
        pass


