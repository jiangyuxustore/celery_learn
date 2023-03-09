from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from blog.models import Article
from blog.customserializers import ArticleSerializer, UserArticleSerializer, UserSerializer
from rest_framework.authentication import BasicAuthentication
from django.contrib.auth.models import User


class ArticleList(APIView):

    authentication_classes = [BasicAuthentication]

    def get(self, request, *args, **kwargs):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            # 注意：手动将request.user与author绑定
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleDetail(APIView):

    def get_object(self, pk):
        try:
            return Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        article = self.get_object(pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        article = self.get_object(pk)
        serializer = ArticleSerializer(instance=article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        article = self.get_object(pk)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserArticleList(APIView):
    def get(self, request, *args, **kwargs):
        user = User.objects.all()
        serializer = UserArticleSerializer(user, many=True, context={"request": request})
        return Response(serializer.data)


class UserArticleDetail(APIView):

    def get_object(self, pk):
        article = Article.objects.get(pk=pk)
        return article

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        article = self.get_object(pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

