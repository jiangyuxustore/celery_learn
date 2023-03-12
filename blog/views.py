from django.http import Http404
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
import math
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from blog.tasks import ArticleOperator, ClassBaseAdd, function_base_add
from blog.models import Article
from blog.customserializers import ArticleSerializer, UserArticleSerializer, UserSerializer
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User


class ArticleList(APIView):
    """同步存储, 当数据存储完成后才返回响应到浏览器"""
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


class AsyncArticleList(APIView):
    """同步存储, 当数据存储完成后才返回响应到浏览器"""
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user.id
        print(user)
        method = request.method
        async_article_operator = ArticleOperator()
        async_article_operator.apply_async(args=(method, data, user))
        msg = {"msg": "接受成功"}
        return Response(msg, status=status.HTTP_200_OK)


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


class CustomNumberPagination(PageNumberPagination):
    """自定义分页类"""

    page_size = 2
    max_page_size = 5
    page_size_query_param = "size"
    page_query_param = "page"

    def get_paginated_response(self, data, cur_page=1):
        """重写父类的方法，自定义返回的字段"""
        return Response(OrderedDict(
            [
                ("count", self.page.paginator.count),
                ("cur_page", cur_page),  # 默认第一页。如果有请求参数，用请求参数
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
                ("total_pages", math.ceil(self.page.paginator.count / self.page_size)),
                ("data", data),
            ]
        ))


class UserArticleList(APIView):
    def get(self, request, *args, **kwargs):
        """分页默认是在GenericAPIView, ViewSet中会使用, 如果使用的是APIView则需要自己实现分页"""
        user = User.objects.all()
        page = CustomNumberPagination()
        page_instance = page.paginate_queryset(queryset=user, request=request, view=self)
        serializer = UserArticleSerializer(page_instance, many=True, context={"request": request})
        return page.get_paginated_response(serializer.data)


# class UserArticleGenericAPIView(GenericAPIView):
#     pagination_class = PageNumberPagination  # GenericAPIView才有pagination_class
#
#     def get(self, request, *args, **kwargs)


class UserArticleDetail(APIView):

    def get_object(self, pk):
        article = Article.objects.get(pk=pk)
        return article

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        article = self.get_object(pk)
        serializer = ArticleSerializer(article)

        return Response(serializer.data)


class AddView(APIView):
    """求和异步任务"""
    def post(self, request, *args, **kwargs):
        x = request.data.get('x', 0)
        y = request.data.get('y', 0)
        class_base_add = ClassBaseAdd()
        class_base_add.apply_async(args=(x, y))
        function_base_add.apply_async(args=(x, str(y)))
        msg = {"msg": "求和任务发送成功"}
        return Response(data=msg)
