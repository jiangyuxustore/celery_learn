import django
import os
from celery import Task
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dxflearn.settings")
django.setup()
from blog import customserializers
from blog import models
from django.contrib.auth.models import User


class ArticleOperator(Task):
    name = "ArticleOperator"

    def get_object(self, pk):
        return models.Article.objects.get(pk=pk)

    def get_user(self, pk):
        return User.objects.get(pk=pk)

    def run(self, method, data, user=None, pk=None, *args, **kwargs):
        if method == "POST":
            serializer = customserializers.ArticleSerializer(data=data)
            user = self.get_user(user)
            if serializer.is_valid():
                # 注意：手动将request.user与author绑定
                serializer.save(author=user)
                return "success"

        elif method == "PUT" and pk is not None:
            article = self.get_object(pk)
            serializer = customserializers.ArticleSerializer(instance=article, data=data)
            if serializer.is_valid():
                serializer.save()
                return "success"

        elif method == "PUT":
            pass

