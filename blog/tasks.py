import django
from celery import Task
django.setup()
from blog import customserializers
from blog import models


class ArticleOperator(Task):
    name = "ArticleOperator"

    def get_object(self, pk):
        return models.Article.objects.get(pk=pk)

    def run(self, method, data, user=None, pk=None, *args, **kwargs):
        if method == "POST":
            serializer = customserializers.ArticleSerializer(data=data)
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

