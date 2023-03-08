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
from steelplate import views

app_name = "steel"  # 指定app_name用户反向生成url

# URL 最好是以^开头, 以$结尾, 新版django如果URL中包含正则那么需要引入re_path
urlpatterns = [
    re_path(r'^(?P<version>[v1|v2]+)/task-list/$', views.TaskList.as_view(), name="task-list"),
    re_path(r'^(?P<version>[v1|v2]+)/task-detail/(?P<pk>[0-9]+)/$', views.TaskDetail.as_view(), name="task-detail"),
]
