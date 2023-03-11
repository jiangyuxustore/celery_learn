# Generated by Django 4.0.8 on 2023-03-08 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SteelOriginalInfo',
            fields=[
                ('task_id', models.CharField(max_length=128, primary_key=True, serialize=False, verbose_name='钢板任务号')),
                ('line_id', models.IntegerField(null=True, verbose_name='输送线id')),
                ('board_thick', models.CharField(max_length=128, null=True, verbose_name='钢板厚度(客户发的)')),
                ('board_type', models.CharField(max_length=128, null=True, verbose_name='钢板型号(客户发的)')),
                ('task_status', models.CharField(max_length=50, verbose_name='任务状态')),
                ('total_count', models.IntegerField(default=0, verbose_name='零件总数量')),
                ('active_count', models.IntegerField(default=0, verbose_name='可分拣零件数')),
                ('success_count', models.IntegerField(default=0, verbose_name='抓取成功数量')),
                ('failed_count', models.IntegerField(default=0, verbose_name='抓取失败取数量')),
                ('json_path', models.CharField(max_length=256, null=True, verbose_name='json图纸的路径')),
                ('dxf_path', models.CharField(max_length=256, null=True, verbose_name='dxf图纸的路径')),
                ('plate_img', models.CharField(max_length=500, null=True, verbose_name='所有工件在整块钢板上的图像路径')),
                ('plate_size', models.CharField(max_length=256, null=True, verbose_name='钢板的尺寸')),
                ('start_time', models.DateTimeField(null=True, verbose_name='任务开始时间')),
                ('end_time', models.DateTimeField(null=True, verbose_name='任务结束时间')),
                ('is_manual_success', models.IntegerField(default=0, verbose_name='是否手动置为成功(0:否, 1:是)')),
                ('is_manual_generate', models.IntegerField(default=0, verbose_name='是否手动生成任务(0:否, 1:是)')),
                ('is_delete', models.IntegerField(default=0, verbose_name='是否删除(0:否, 1:是)')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name_plural': '钢板原始信息表',
                'db_table': 'steel_original_info',
            },
        ),
    ]