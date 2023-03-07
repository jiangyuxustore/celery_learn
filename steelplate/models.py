from django.db import models
import datetime


class SteelOriginalInfo(models.Model):
    """
    我司内部定义的原始钢板任务表
    # wait ready executed success failed.
    # 中控下发任务后初始状态都是wait.
    # vision，viz解析完成返回数据后状态更新为ready，ready状态的任务可以开始也可以停止.
    # 当任务开始时，状态更新为--> executed，当任务停止时，状态更新为-->failed ，已经开始的任务只能停止，无法继续开始.
    """

    task_id = models.CharField(max_length=128, primary_key=True, verbose_name="钢板任务号")
    line_id = models.IntegerField(null=True, verbose_name="输送线id")
    board_thick = models.CharField(max_length=128, null=True, verbose_name="钢板厚度(客户发的)")
    board_type = models.CharField(max_length=128, null=True, verbose_name="钢板型号(客户发的)")
    task_status = models.CharField(max_length=50, null=False, verbose_name="任务状态")
    total_count = models.IntegerField(default=0, null=False, verbose_name="零件总数量")  # 客户图纸里面包含partSize 1,2,3的零件数
    active_count = models.IntegerField(default=0, verbose_name="可分拣零件数")  # vision解析后返回的可分拣零件数
    success_count = models.IntegerField(default=0, null=False, verbose_name="抓取成功数量")
    failed_count = models.IntegerField(default=0, null=False, verbose_name="抓取失败取数量")
    json_path = models.CharField(max_length=256, null=True, verbose_name="json图纸的路径")
    dxf_path = models.CharField(max_length=256, null=True, verbose_name="dxf图纸的路径")
    plate_img = models.CharField(max_length=500, null=True, verbose_name="所有工件在整块钢板上的图像路径")
    plate_size = models.CharField(max_length=256, null=True, verbose_name="钢板的尺寸")  # vision解析工程会返回这个字段
    start_time = models.DateTimeField(null=True, verbose_name="任务开始时间")
    end_time = models.DateTimeField(null=True, verbose_name="任务结束时间")
    is_manual_success = models.IntegerField(default=0, null=False, verbose_name="是否手动置为成功(0:否, 1:是)")
    is_manual_generate = models.IntegerField(default=0, null=False, verbose_name="是否手动生成任务(0:否, 1:是)")
    is_delete = models.IntegerField(default=0, null=False, verbose_name="是否删除(0:否, 1:是)")
    created_time = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        """元数据"""

        db_table = "steel_original_info"
        verbose_name_plural = "钢板原始信息表"


class SteelWorkpieceCommonInfo(models.Model):
    """SteelWorkpieceCommonInfo table"""

    part_name = models.CharField(max_length=128, primary_key=True, verbose_name="磁吸类型名")
    solid_cloud_img = models.CharField(max_length=500, null=True, verbose_name="实心点云图片路径(单个小钢板的图片)")  # 共有 给前端用实心点云路径
    contour_cloud_img = models.CharField(max_length=500, null=True, verbose_name="空心点云图片路径(单个小钢板的图片)")  # 共有
    pick_point_2d = models.CharField(max_length=128, null=True, verbose_name="物体坐标系下2d抓取点")  # 共有
    pick_point_with_sucker = models.CharField(max_length=128, null=True, verbose_name="物体包含吸盘坐标系下的抓取点")
    object_with_sucker_img = models.CharField(max_length=500, null=True, verbose_name="磁吸配置图片路径")  # 共有
    object_bounding_rect = models.CharField(max_length=128, null=True, verbose_name="工件外接矩形")  # 共有
    # 物体自身的geo_center
    geo_center_in_object = models.CharField(max_length=256, null=True, verbose_name="该类型工件自身的geo_center")
    geo_center_in_object_3d = models.CharField(max_length=256, null=True, verbose_name="该类型工件自身的3d geo_center")
    # 共有由原先的独有信息变成公有信息
    bounding_rect_with_gripper = models.CharField(max_length=128, null=True, verbose_name="携带夹具的工件外接矩形")
    thickness = models.FloatField(default=0, verbose_name="厚度（单位mm）")  # 共有
    weight = models.FloatField(default=0, verbose_name="重量（单位kg）")  # 共有
    catcher_switch = models.CharField(max_length=128, null=True, verbose_name="磁吸阵列开关")
    is_deprecated = models.IntegerField(default=0, null=False, verbose_name="是否弃用(0:否, 1:是)")  # 删除的工件类型关联的实例都不分拣
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        """元数据"""

        db_table = "steel_workpiece_common_info"
        verbose_name_plural = "钢板类型公有表"


class SteelWorkPieceInstanceInfo(models.Model):
    """钢板实例表"""

    task = models.ForeignKey("SteelOriginalInfo", on_delete=models.CASCADE, verbose_name="钢板任务号")
    instance_name = models.CharField(max_length=128, primary_key=True, verbose_name="实例唯一编号")
    material_id = models.CharField(max_length=100, null=True, verbose_name="零件物料ID号")
    part_size = models.CharField(max_length=50, null=True, verbose_name="零件大小(默认为大)")  # 客户方的大小类型，筛选完成part_size都是3
    part_name = models.ForeignKey("SteelWorkpieceCommonInfo", on_delete=models.CASCADE, verbose_name="类型公有信息")
    part_name_to_viz = models.CharField(max_length=256, null=True, verbose_name="发送给viz在线规划的part_name")
    # 物体在整块钢板上的geo_center
    object_in_whole = models.CharField(max_length=256, null=True, verbose_name="该物体实例在整块钢板的位置")
    object_in_plate_3d = models.CharField(max_length=256, null=True, verbose_name="物体geo在钢板坐标系下的3d位姿")
    geo_with_rotation_in_plate = models.CharField(max_length=256, null=True, verbose_name="物体在钢板坐标系下的3d带角度位姿")
    object_in_plate_img = models.CharField(max_length=500, null=True, verbose_name="小工件在整块钢板上的图像路径")  # 独有
    place_point_in_pallet = models.CharField(max_length=256, null=True, verbose_name="viz托盘坐标系下的放置点")  # viz返回
    place_point_3d = models.CharField(
        max_length=256, null=True, verbose_name="vision转换viz的坐标"
    )  # viz返回这个字段是从place_point_in_pallet转换来的
    orientation = models.CharField(max_length=45, null=True, verbose_name="viz解析出的方向")  # viz返回
    picked_poses = models.CharField(max_length=256, null=True, verbose_name="viz解析出的抓取点")  # viz返回
    #  独有，这个我司内部判断的大于3000大件，800-3000中件，800以下小件
    size_type = models.CharField(max_length=45, null=True, verbose_name="尺寸类型(big大件/middle中件/small小件)")
    is_angle_within_range = models.CharField(
        max_length=45, default="1", null=True, verbose_name="工件倾斜角度是否在阈值内"
    )  # 0否，1是
    device = models.ForeignKey("palletmanager.ExecDevice", null=True, on_delete=models.CASCADE)
    pallet_berth = models.ForeignKey("palletmanager.PalletBerth", null=True, on_delete=models.CASCADE)
    tray_id = models.CharField(max_length=50, null=True, verbose_name="工件放置的托盘号id")
    sub_task_status = models.CharField(max_length=50, null=True, verbose_name="子任务状态")
    act_pick_point = models.CharField(max_length=256, null=True, verbose_name="实际抓取点")
    act_place_point = models.CharField(max_length=256, null=True, verbose_name="实际放置点")
    enqueue_time = models.DateTimeField(null=True, verbose_name="入队时间")  # 工件系统分发的时间
    executed_time = models.DateTimeField(null=True, verbose_name="开知执行时间")  # 工控机开始执行任务的时间
    end_time = models.DateTimeField(null=True, verbose_name="结束时间")  # 这个不管任务成功失败还是取消还是手动，只要停下就结束
    is_manual_success = models.IntegerField(default=0, null=False, verbose_name="是否手动置为成功(0:否, 1:是)")
    is_delete = models.IntegerField(default=0, null=False, verbose_name="是否删除(0:否, 1:是)")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        """元数据"""

        db_table = "steel_workpiece_instance_info"
        verbose_name_plural = "钢板工件实例信息表"


class MagneticJson(models.Model):
    """该表只存一个字段，ee2.json"""

    id = models.AutoField(primary_key=True, verbose_name="自增主键")
    json_response = models.TextField(verbose_name="ee2.json数据")

    class Meta:
        """元数据"""

        db_table = "steel_magnetic_json"
        verbose_name_plural = "vision json配置表"


class ConveyorLineInfo(models.Model):
    """输送线的一些信息"""

    line_id = models.IntegerField(primary_key=True, verbose_name="输送线id")
    berth_id = models.CharField(max_length=128, null=False, verbose_name="泊位编号")
    ipc_ip = models.CharField(max_length=128, null=False, verbose_name="输送线上工控机的ip")

    class Meta:
        """元数据"""

        db_table = "steel_conveyor_line_info"
        verbose_name_plural = "钢板输送线信息表"


class MaterialId(models.Model):
    """material id model"""

    pk = models.IntegerField(primary_key=True, verbose_name="主键id")
    material_id = models.CharField(max_length=128, null=False, verbose_name="material id")
