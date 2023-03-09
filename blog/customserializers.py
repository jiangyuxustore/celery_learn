from rest_framework import serializers
from blog.models import Article, ArticleAttr
from django.contrib.auth import get_user_model


User = get_user_model()


class BodyValidator(object):
    """第三种验证方式类验证器, 这个会放到字段中"""
    def get_validator(self, is_accurate=False):
        """
        是否精确验证, is_accurate=True则返回精确验证器, is_accurate=False则返回模糊验证器
        :param is_accurate:
        :return:
        """
        if is_accurate:
            print("返回精确验证器")
            return "精确验证器对象"
        print("模糊验证器对象")
        return "模糊验证器对象"

    def __call__(self, value):
        length = len(value)
        if length > 1000:
            validator = self.get_validator(True)
        else:
            validator = self.get_validator(False)

        return value


class MyField(serializers.ReadOnlyField):

    def to_representation(self, value):
        if value:
            return "是"
        return "否"


class ArticleSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=True, max_length=90)
    body = serializers.CharField(required=False, allow_blank=True, validators=[BodyValidator()])
    author = serializers.ReadOnlyField(source="author.id")
    user_type = serializers.SerializerMethodField()
    # source的作用是关联数据库的字段, author.is_superuser关联到author表中的is_superuser字段, 下面是关联到username字段
    # is_superuser = serializers.ReadOnlyField(source="author.is_superuser")
    is_superuser = MyField(source="author.is_superuser")
    # source的作用是关联数据库的字段, author.username关联到author表中的username字段
    username = serializers.ReadOnlyField(source="author.username")
    status = serializers.ReadOnlyField(source="get_status_display")
    create_date = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        """
        继承Serializer类, 需要重写两个方法, 第一个是create方法, 第二个就是update方法, create方法用来创建对象
        之所以要重写该方法有一个场景就是我们要创建多个对象, 比如在创建文章的同时我也要统计一下文章的字符个数
        :param validated_data:
        :return:
        """
        article = Article.objects.create(**validated_data)
        title_length = len(validated_data.get("title", ""))
        body_length = len(validated_data.get("body", ""))
        article_attr = ArticleAttr(article.id, title_length, body_length)
        article_attr.save()
        return article

    def update(self, instance, validated_data):
        """
        继承Serializer类, 需要重写两个方法, 第一个是create方法, 第二个就是update方法, update方法用来更新对象
        比如用户在更新文的时候, 我们同步也要更新文章属性表中标题长度和body长度.
        create方法和update方法有很大的关联性, 在实例化序列化器类的时候存在以下两种情况:
            s1 = ArticleSerializer(data=request.data), 这种情况下调用s1.save()方法那最终会执行create方法
            s2 = ArticleSerializer(instance=article, data=request.data), 这种情况下调用s2.save()方法那最终会执行update方法
        :param instance:
        :param validated_data:
        :return:
        """
        instance.title = validated_data.get("title", instance.title)
        instance.body = validated_data.get("body", instance.body)
        instance.status = validated_data.get("status", instance.status)
        instance.save()
        article_attr = ArticleAttr.objects.get(pk=instance.id)
        article_attr.title_length = len(instance.title)
        article_attr.body_length = len(instance.body)
        article_attr.save()
        return instance

    def validate_title(self, value):
        """
        第一种字段级别的验证, 定义validate_<field_name>方法
        :param value: 传进来进行验证的title字段的值
        :return:
        """
        print("验证titile")
        if "django" not in value.lower():
            raise serializers.ValidationError("标题必须包含django字符")
        return value

    def validate(self, attrs):
        """
        第二种数据验证方式
        :param attrs:
        :return:
        """
        print("全属性验证, 字典的值:{}".format(attrs))
        body = attrs['body']
        print("验证body字段")
        return attrs

    def get_user_type(self, obj):
        """
        SerializerMethodField字段是一个只读字段, 这个字段有一个作用就是可以定义一个get_<file_name>方法来自定义
        返回的内容, 比如上面定义了user_type = serializers.SerializerMethodField(), 则此处需要定义get_user_type方法
        :param obj:
        :return:
        """
        if obj.author.is_superuser:
            return "超级管理员"
        else:
            return "普通用户"

    def to_representation(self, instance):
        """
        我们在上面定义了一些字段, 这里我们为返回的结果新增了一个desc字段用来描述当前文章的简要
        因为之前定义的文章没有存储属性数据, 所以只能访问特定的谋篇文章才能拿到body_length等数据
        http://127.0.0.1:8000/blog/api/v1/articles/8/
        :param instance:
        :return:
        """
        data = super().to_representation(instance)
        if hasattr(instance, "articleattr"):
            body_length = instance.articleattr.body_length
            data["desc"] = "作者:{}写了一篇名为:{}的文章, 文章的总字数:{}".format(instance.author, instance.title, body_length)
        return data


# class ArticleSerializer(serializers.ModelSerializer):
#     """这种序列化器是直接继承ModelSerializer, 然后在Meta中定义这个ModelSerializer的属性"""
#     class Meta:
#         model = Article
#         # 这里的fields有两种用法, 第一种是设置为__all__还有一种是自定义要显示的字段
#         fields = ['id', 'title', 'body', 'status', 'create_date', 'author']
#         # fields = '__all__'
#         # 所有字段都列出, 但id, author, create_date是只读字段
#         read_only_fields = ('id', 'author', 'create_date')
#         depth = 1  # 注意这里


class UserSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    is_superuser = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()

#
#
# class ArticleSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     title = serializers.CharField(required=True, allow_blank=True, max_length=90)
#     body = serializers.CharField(required=False, allow_blank=True, validators=[BodyValidator()])
#     status = serializers.ReadOnlyField(source="get_status_display")
#     author = UserSerializer()
#     create_date = serializers.DateTimeField(read_only=True)


class UserArticleSerializer(serializers.ModelSerializer):
    # PrimaryKeyRelatedField 会将User发表的文章关联出来, 但这个显示的是文章的主键id
    # articles = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # StringRelatedField 会将User发表的文章关联出来, 同时显示的内容是Article的__str__方法返回的值
    # articles = serializers.StringRelatedField(many=True, read_only=True)
    # HyperlinkedRelatedField会生成关联的URL, 但这里的view_name需要注意的是一定加app_name也就是blog
    articles = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='blog:user-article-detail'
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'articles',)
        read_only_fields = ('id', 'username',)
