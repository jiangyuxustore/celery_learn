"""权限模块"""

from rest_framework.permissions import BasePermission


class SuperPermission(BasePermission):
    """定义超级用户才能访问"""
    message = "必须是超级用户才能访问"

    def has_permission(self, request, view):
        """
        has_permission作用域是视图, 返回True意味着对该视图有访问权限, 返回False则没有权限
        如果账号密码是redis, redis的用户是验证不通过的
        如果账号密码是root, root的用户是验证通过的
        :param request:
        :param view:
        :return:
        """
        is_superuser = request.user.is_superuser
        if is_superuser:
            return True
        else:
            return False

