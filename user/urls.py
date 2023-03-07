"""dxflearn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from user import views

app_name = "user"  # 指定app_name用户反向生成url

# URL 最好是以^开头, 以$结尾, 新版django如果URL中包含正则那么需要引入re_path
urlpatterns = [
    re_path(r'^(?P<version>[v1|v2]+)/register/$', views.Register.as_view()),
    re_path(r'^v1/email-verify/$', views.EmailVerify.as_view()),
    re_path(r'^v1/login/$', views.Login.as_view()),
    re_path(r'^v1/order/$', views.OrderList.as_view()),
    re_path(r'^v1/order-detail/$', views.OrderDetail.as_view()),
    re_path(r'^(?P<version>[v1|v2]+)/list/$', views.UserList.as_view(), name="list"),
    re_path(r'^(?P<version>[v1|v2]+)/detail/(?P<pk>[0-9]+)/$', views.UserInfo.as_view(), name="detail"),
]
