from rest_framework import serializers
from steelplate import models


class SteelOriginalInfoSerializer(serializers.Serializer):
    task_id = serializers.CharField(max_length=128)
    line_id = serializers.IntegerField()
    board_thick = serializers.CharField(max_length=128)
    board_type = serializers.CharField(max_length=128)
    task_status = serializers.CharField(max_length=50)
    total_count = serializers.IntegerField(default=0)
    active_count = serializers.IntegerField(default=0)
    success_count = serializers.IntegerField(default=0)
    failed_count = serializers.IntegerField(default=0)
    json_path = serializers.CharField(max_length=256)
    dxf_path = serializers.CharField(max_length=256)
    plate_img = serializers.CharField(max_length=500)
    plate_size = serializers.CharField(max_length=256)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    is_manual_success = serializers.IntegerField(default=0)
    is_manual_generate = serializers.IntegerField(default=0)
    is_delete = serializers.IntegerField(default=0)

    class Meta:
        model = models.SteelOriginalInfo
        fields = "__all__"
        ordering = ["created_time"]
