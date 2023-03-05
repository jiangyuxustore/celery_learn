from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):
    """订单表"""
    order_id = models.BigAutoField(primary_key=True, verbose_name="主键订单号")
    order_amount = models.FloatField(verbose_name="订单金额")
    order_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="下单的用户名")
    order_status = models.IntegerField(default=1, verbose_name="订单状态")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="订单创建时间")

    class Meta:
        db_table = "order_info"
