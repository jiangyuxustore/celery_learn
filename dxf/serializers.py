"""序列化类模块."""
from rest_framework import serializers
from django.contrib.auth.models import User


class OrderSerializer(serializers.Serializer):
    order_id = serializers.CharField(max_length=256, primary_key=True)
    order_amount = serializers.FloatField()
    order_user = serializers.ForeignKey(User, on_delete=models.CASCADE, verbose_name="下单的用户名")
    order_status = serializers.IntegerField(default=1)
    create_time = serializers.DateTimeField(auto_now_add=True)

