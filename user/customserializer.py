"""序列化模块"""

from rest_framework import serializers
from user.models import Order


class OrderSerializer(serializers.ModelSerializer):

    order_user = serializers.ReadOnlyField(source="User.username")

    class Meta:
        model = Order
        fields = ["order_id", "order_amount", "order_user", "order_status", "create_time"]


