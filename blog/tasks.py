import django
from celery import Task
django.setup()
from blog import customserializers
from blog import models

class ArticleOperator(Task):
    name = "ArticleOperator"

    def get_object(self, pk):
        return models.Article.objects.get(pk=pk)
    def run(self, method, data, pk=None, *args, **kwargs):
        if method == "POST":


        elif method == "PUT" and pk is not None:
            article = self.get_object(pk)
            serializer = customserializers.ArticleSerializer(instance=article, data=data)
            if serializer.is_valid():
                serializer.save()

        elif method == "PUT":
            pass

