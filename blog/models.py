from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Article(models.Model):

    STATUS_CHOICES = (
        ("p", "Published"),
        ("d", "Draft")
    )

    title = models.CharField(verbose_name='Title', max_length=90, db_index=True)
    body = models.TextField(verbose_name='Body', blank=True)
    author = models.ForeignKey(User, verbose_name='Author', on_delete=models.CASCADE, related_name='articles')
    status = models.CharField(verbose_name='Status', max_length=1, choices=STATUS_CHOICES, default='s', null=True, blank=True)
    create_date = models.DateTimeField(verbose_name='Create Date', auto_now_add=True)

    def __str__(self):
        """__str__方法是作用于str(article_instance)时会输出article_instance的title"""
        return self.title

    class Meta:
        ordering = ['-create_date']
        verbose_name = "Article"
        verbose_name_plural = "Article"


class ArticleAttr(models.Model):
    id = models.OneToOneField("Article", primary_key=True, on_delete=models.CASCADE)
    title_length = models.IntegerField(verbose_name="标题的字符个数")
    body_length = models.IntegerField(verbose_name="body的字符个数")
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return "title_length:{}, body_length:{}".format(self.title_length, self.body_length)
