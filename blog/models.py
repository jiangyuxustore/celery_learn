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
    status = models.CharField('Status', max_length=1, choices=STATUS_CHOICES, default='s', null=True, blank=True)
    create_date = models.DateTimeField(verbose_name='Create Date', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        order = ['-create_date']
        verbose_name = "Article"
        verbose_name_plural = "Article"
