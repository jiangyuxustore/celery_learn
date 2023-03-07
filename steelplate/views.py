# import datetime
# import math
# from collections import OrderedDict
# import requests
# import shutil
# import json
# from utils import messages
from rest_framework.views import APIView
# from rest_framework.pagination import PageNumberPagination
# from rest_framework import serializers
# from utils.grpc_service import scheduler_center
# from utils.logcreator import view_log, san_yi_log
# from utils.logcreator import log_folder
# from utils.drawparse import parse_center
# from utils.public import view_wrapper, syview_wrapper
# from utils import systatus
# from utils.externalcommunication import wcs
# import os
# from steelplate import models
# from mechmind import settings
# import re
#
#
# class PalletNumberPagination(PageNumberPagination):
#     """分页类"""
#
#     page_size = 20
#     max_page_size = 10
#     page_size_query_param = "size"
#     page_query_param = "page"
#
#     def get_paginated_response(self, data, cur_page=1):
#         """重写父类的方法，增加一个total_page字段"""
#         return OrderedDict(
#             [
#                 ("count", self.page.paginator.count),
#                 ("cur_page", cur_page),  # 默认第一页。如果有请求参数，用请求参数
#                 ("total_pages", math.ceil(self.page.paginator.count / self.page_size)),
#                 ("tasks", data),
#             ]
#         )
#
#
# class PagerSerializer(serializers.ModelSerializer):
#     """序列化类"""
#
#     class Meta:
#         """meta 信息"""
#
#         model = models.SteelOriginalInfo
#         fields = "__all__"
#         ordering = ["id"]
#
#
# class ChildTask(APIView):
#     """子任务的操作"""
#
#     @view_wrapper
#     def get(self, request, *args, **kwargs):
#         """子任务查询, 根据父任务task_id查询关联的子任务清单."""
#         response_data = {}
#         query_params = dict(request.query_params.items())
#         task_id = query_params.pop("task_id")
#         task_instance = models.SteelOriginalInfo.objects.get(task_id=task_id)
#         response_data["task_id"] = task_id
#         response_data["task_status"] = task_instance.task_status
#         subtasks = []
#         for item in task_instance.steelworkpieceinstanceinfo_set.all().filter(is_delete=0):
#             device_name = "未关联" if item.device is None else item.device.device_name
#             act_pick_point = item.act_pick_point
#             act_place_point = item.act_place_point
#             act_pick_point = [] if act_pick_point is None else eval(act_pick_point)
#             act_place_point = [] if act_place_point is None else eval(act_place_point)
#             msg = dict(
#                 instance_name=item.instance_name,
#                 part_name=item.part_name.part_name,
#                 object_mask_path=item.part_name.solid_cloud_img,
#                 object_in_plate_img=item.object_in_plate_img,
#                 weight=item.part_name.weight,
#                 sub_task_status=item.sub_task_status,
#                 equipment_number=device_name,
#                 act_pick_point=act_pick_point,
#                 act_place_point=act_place_point,
#                 magnetic_details_image_path=item.part_name.object_with_sucker_img,  # 磁吸阵列图
#                 executed_time=item.executed_time,
#                 end_time=item.end_time,
#             )
#             subtasks.append(msg)
#         response_data["subtasks"] = subtasks
#         return response_data
#
#     @view_wrapper
#     def delete(self, request, *args, **kwargs):
#         """删除接口"""
#         request_data = request.data["request_data"]
#         task_id = request_data["task_id"]
#         instance = models.SteelOriginalInfo.objects.get(task_id=task_id)
#         task_status = instance.task_status
#         if task_status in (messages.TASK_EXECUTED, messages.TASK_MODIFY):
#             raise systatus.AppException(systatus.EXECUTED_OR_MODIFY_TASK_CAN_NOT_DELETE)
#         instance_list = request_data["instance_list"]
#
#         workpiece_query_set = instance.steelworkpieceinstanceinfo_set.all()
#         for instance_name in instance_list:
#             workpiece_instance = workpiece_query_set.filter(instance_name=instance_name)[0]
#             workpiece_instance.is_delete = 1
#             workpiece_instance.save()
#         response_msg = {"instance_list": instance_list, "msg": "删除成功"}
#         return response_msg
#
#     @view_wrapper
#     def put(self, request, *args, **kwargs):
#         """更新接口"""
#         request_data = request.data["request_data"]
#         task_id = request_data["task_id"]
#         instance_name = request_data["instance_name"]
#         update_fields = request_data["update_fields"]
#         view_log.info(
#             "修改工件实例, task_id:{}, instance_name:{}, update_fields:{}".format(task_id, instance_name, update_fields)
#         )
#         instance = models.SteelOriginalInfo.objects.get(task_id=task_id)
#         task_status = instance.task_status
#         if task_status == messages.TASK_EXECUTED:
#             raise systatus.AppException(systatus.EXECUTED_TASK_CAN_NOT_MODIFY)
#         workpiece_instance = instance.steelworkpieceinstanceinfo_set.all().filter(instance_name=instance_name)
#         workpiece_instance.update(**update_fields)
#         response_msg = {"task_id": task_id, "instance_name": instance_name, "msg": "工件实例字段修改成功"}
#         return response_msg
#
#
# class Task(APIView):
#     """与中控系统交互的接口, 中控系统通过此接口下发任务, 查询任务"""
#
#     @view_wrapper
#     def get(self, request, *args, **kwargs):
#         """
#         历史任务查询, 查询所有或按照查询条件进行按条件返回。返回的结果是表steel_original_info中的数据
#         @ demo
#         @ url http://127.0.0.1:8000/steelplate/api/v1/task #返回所有的父任务的信息，这个是默认的
#               http://127.0.0.1:8000/steelplate/api/v1/task?page=2 #查询下一页数据，只需要修改page参数即可
#               http://127.0.0.1:8000/steelplate/api/v1/task?task_status=success&page=2 #查询任务状态为success的第二页的数据
#               http://127.0.0.1:8000/steelplate/api/v1/task?task_id=975c28ec-79c4-11ec-9b30-f47b09172194 # 根据任务号进行查询
#               http://127.0.0.1:8000/steelplate/api/v1/task?task_status=success #查询任务状态为success的数据
#         """
#         query_params = dict(request.query_params.items())
#         cur_page = int(query_params.pop("page", 1))
#         query_params.pop("size", 404)
#         if len(query_params) == 0:
#             data = models.SteelOriginalInfo.objects.all().filter(is_delete=0).order_by("-created_time")
#         else:
#             data = models.SteelOriginalInfo.objects.filter(**query_params).filter(is_delete=0).order_by("-created_time")
#         page = PalletNumberPagination()
#         page_instance = page.paginate_queryset(queryset=data, request=request, view=self)
#         pallet_data = PagerSerializer(instance=page_instance, many=True)
#         return page.get_paginated_response(pallet_data.data, cur_page)
#
#     @syview_wrapper
#     def post(self, request, *args, **kwargs):
#         """任务下发，启动任务."""
#         request_data = request.data.get("requestData")
#         task_id = request_data.get("taskID")
#         task_status = request_data["taskStatus"]
#         if task_status == 0:
#             self.download_file(task_id=task_id, request_data=request_data)
#             response_msg = {"task_id": task_id, "msg": "接收图纸解析任务成功"}
#         elif task_status == 1:
#             line_id = int(request_data.get("lineID"))
#             self.before_start_check(task_id, line_id)
#             start_strategy = request_data.get("start_strategy", "generate")
#             instance = models.SteelOriginalInfo.objects.get(task_id=task_id)
#             task_status = instance.task_status
#             is_delete = instance.is_delete
#             if task_status == messages.TASK_MODIFY:
#                 raise systatus.AppException(systatus.MODIFY_TASK_CAN_NOT_START)
#             elif task_status == messages.TASK_WAIT:
#                 raise systatus.AppException(systatus.WAIT_TASK_CAN_NOT_START)
#             if is_delete:
#                 raise systatus.AppException(systatus.DELETE_TASK_CAN_NOT_START)
#             scheduler_center.start_task(task_id, line_id, start_strategy)
#             san_yi_log.info("中控下发{}线启动钢板分拣, 任务号:{}".format(line_id, task_id))
#             response_msg = {"task_id": task_id, "msg": "启动任务成功"}
#         return response_msg
#
#     def before_start_check(self, task_id, line_id):
#         """启动任务前的检查"""
#         try:
#             instance = models.SteelOriginalInfo.objects.get(task_id=task_id)
#             task_status = instance.task_status
#             if task_status == messages.TASK_WAIT:
#                 raise systatus.AppException(systatus.WAIT_TASK_CAN_NOT_START)
#         except Exception as e:
#             context = {
#                 "task_id": task_id,
#                 "line_id": line_id,
#                 "total_count": 0,
#                 "active_count": 0,
#                 "success_count": 0,
#                 "status": 1,
#                 "part_list": [],
#             }
#             wcs.done_callback(context)
#
#     def download_file(self, task_id, request_data):
#         """下载json图纸/dxf图纸"""
#         current_date = datetime.datetime.now().strftime("%Y-%m-%d")
#         common_info_dir = settings.COMMON_INFO_DIR
#         private_info_dir = settings.PRIVATE_INFO_DIR
#         file_write_path = os.path.join(private_info_dir, current_date, task_id)
#         if not os.path.exists(file_write_path):
#             os.makedirs(file_write_path)
#         json_url = settings.JSON_URL + "{}.json".format(task_id)
#         dxf_url = settings.DXF_URL + "{}.dxf".format(task_id)
#         json_path = self.download(json_url, file_write_path)
#         filter_json_path, total_count, active_count = self.filter_big_steel(json_path)
#         dxf_path = self.download(dxf_url, file_write_path)
#         request_data["active_count"] = active_count
#         request_data["total_count"] = total_count
#         request_data["json_path"] = json_path
#         request_data["file_write_path"] = file_write_path
#         request_data["common_info_dir"] = common_info_dir
#         request_data["filter_json_path"] = filter_json_path
#         request_data["dxf_path"] = dxf_path
#         self.save_to_mysql(request_data)
#
#     def save_to_mysql(self, request_data):
#         """将中控发送的任务写入mysql"""
#         task_id = request_data.get("taskID")
#         board_thick = request_data.get("boardThick")
#         board_type = request_data.get("boardType")
#         file_write_path = request_data["file_write_path"]
#         common_info_dir = request_data["common_info_dir"]
#         json_path = request_data["json_path"]
#         filter_json_path = request_data["filter_json_path"]
#         dxf_path = request_data["dxf_path"]
#         total_count = request_data["total_count"]
#         active_count = request_data["active_count"]
#         steel_original_info = models.SteelOriginalInfo(
#             task_id=task_id,
#             task_status="wait",
#             total_count=total_count,
#             active_count=active_count,
#             board_thick=board_thick,
#             board_type=board_type,
#             json_path=filter_json_path,
#             dxf_path=dxf_path,
#             created_time=str(datetime.datetime.now()),
#         )
#         steel_original_info.save()
#
#         msg = {
#             "file_write_path": file_write_path,
#             "filter_json_path": filter_json_path,
#             "json_path": json_path,
#             "dxf_path": dxf_path,
#             "common_info_dir": common_info_dir,
#         }
#         vision_msg = messages.ServerAdapterMessageTemplate(receiver=("vision", "viz"), task_id=task_id, msg=msg)
#         parse_center.submit_task_to_parse(vision_msg, orientation="left")
#         san_yi_log.info("中控下发图纸解析, 任务号:{}, 任务成功推送到任务队列".format(task_id))
#
#     def download(self, request_url, file_write_path=None):
#         """
#         :param request_url: str, 中控下载文件的url
#         :param file_write_path: str, 获取到的文件写到何处
#         :return:
#         """
#         response = requests.get(request_url)
#         filename = os.path.basename(request_url)
#         if response.status_code == 200:
#             fullpath = os.path.join(file_write_path, filename)
#             with open(fullpath, "wb") as f:
#                 f.write(response.content)
#             return fullpath
#         else:
#             raise systatus.AppException(systatus.DOWNLOAD_FILE_FAILED)
#
#     def filter_big_steel(self, path):
#         """筛选出大件"""
#         with open(path, "r", encoding="utf-8") as f:
#             data = json.loads(f.read())
#             part_list = []
#             total_count = len(data["PartList"])
#             for item in data["PartList"]:
#                 if item["PartSize"] == 3:
#                     part_list.append(item)
#             data["PartList"] = part_list
#             active_count = len(part_list)
#         dir_path = os.path.dirname(path)
#         file_name = "filter" + os.path.basename(path)
#         filter_json_path = os.path.join(dir_path, file_name)
#         with open(filter_json_path, "w+", encoding="utf-8") as f:
#             f.write(json.dumps(data, ensure_ascii=False))
#         return filter_json_path, total_count, active_count
#
#     @staticmethod
#     def clear_adapter_log_file():
#         """清空日志文件"""
#         file_list = os.listdir(log_folder)
#         for file in file_list:
#             current_date = datetime.date.today()
#             file_date_str = re.search(r"(\d+-\d+-\d+)", file).group(1)
#             file_date = datetime.datetime.strptime(file_date_str, "%Y-%m-%d").date()
#             diff_day = (current_date - file_date).days
#             if diff_day > 3:
#                 log_file_path = os.path.join(log_folder, file)
#                 os.remove(log_file_path)
#
#     @view_wrapper
#     def delete(self, request, *args, **kwargs):
#         """删除接口"""
#         request_data = request.data["request_data"]
#         task_list = request_data["task_list"]
#         view_log.info("删除切割任务, task_list:{}".format(task_list))
#         delete_task_list = []
#         for task_id in task_list:
#             instance = models.SteelOriginalInfo.objects.get(task_id=task_id)
#             task_status = instance.task_status
#             if task_status == messages.TASK_EXECUTED:
#                 continue
#             instance.is_delete = 1
#             instance.save()
#             delete_task_list.append(task_id)
#         response_msg = {"task_id": delete_task_list, "msg": "删除成功"}
#         return response_msg
#
#     @view_wrapper
#     def put(self, request, *args, **kwargs):
#         """更新接口"""
#         request_data = request.data["request_data"]
#         task_id = request_data["task_id"]
#         update_fields = request_data["update_fields"]
#         view_log.info("修改切割任务, task_id:{}, update_fields:{}".format(task_id, update_fields))
#         instance = models.SteelOriginalInfo.objects.get(task_id=task_id)
#         task_status = instance.task_status
#         if task_status == messages.TASK_EXECUTED:
#             raise systatus.AppException(systatus.EXECUTED_TASK_CAN_NOT_MODIFY)
#         instance.task_status = messages.TASK_MODIFY
#         instance.__dict__.update(**update_fields)
#         instance.save()
#         response_msg = {"task_id": task_id, "msg": "任务被重置为修改状态"}
#         return response_msg
#
#
# class MagneticAttraction(APIView):
#     """磁吸配置接口"""
#
#     @view_wrapper
#     def get(self, request, *args, **kwargs):
#         """
#         获取磁吸配置
#         @ demo
#         @ url: http://127.0.0.1:8000/steelplate/api/v1/magnetic-suction?part_name=SY365CGI3K-3-4-1-1-2
#         """
#         query_params = dict(request.query_params.items())
#         part_name = query_params["part_name"]
#         view_log.info("获取磁吸配置, 前端传入的part_name:{}".format(part_name))
#         instance = models.SteelWorkpieceCommonInfo.objects.get(part_name=part_name)
#         magnetic_instance = models.MagneticJson.objects.get(id=1)
#         object_bounding_rect = eval(instance.object_bounding_rect)
#         object_with_sucker_img = instance.object_with_sucker_img
#         pick_point_2d = eval(instance.pick_point_2d)
#         catcher_switch = eval(instance.catcher_switch)
#         catcher_switch_size = len(catcher_switch)
#         magnetic_json = eval(magnetic_instance.json_response)
#         workpiece = dict(
#             part_name=part_name,
#             object_mask_path=instance.solid_cloud_img,
#             width=object_bounding_rect[0],
#             height=object_bounding_rect[1],
#             pick_point_2d=pick_point_2d,
#             object_with_sucker_img=object_with_sucker_img,
#             catcher_switch_size=catcher_switch_size,
#             catcher_switch=catcher_switch,
#             upper_left_x="未知",
#             upper_left_y="未知",
#         )
#         result = dict(workpiece=workpiece, magnetic=magnetic_json)
#         return result
#
#     @view_wrapper
#     def post(self, request, *args, **kwargs):
#         """
#         修改磁吸配置, 保存到数据库后发给viz重新进行码垛规划
#         @ demo
#         @ url: http://127.0.0.1:8000/steelplate/api/v1/magnetic-suction
#         """
#         request_data = request.data["request_data"]
#         part_name = request_data["part_name"]
#         pick_point_2d = str(request_data["magnetic_setting"]["pick_point_2d"])
#         object_with_sucker_img = request_data["magnetic_setting"]["object_with_sucker_img"]
#         pick_point_with_sucker = str(request_data["magnetic_setting"]["pick_point_with_sucker"])
#         bounding_rect_with_gripper = str(request_data["magnetic_setting"]["bounding_rect_with_gripper"])
#         catcher_switch = str(request_data["magnetic_setting"]["catcher_switch"])
#         view_log.info(
#             "修改磁吸配置, 前端传入的part_name:{}, pick_point_2d:{}, object_with_sucker_img:{}, "
#             "pick_point_with_sucker:{}, bounding_rect_with_gripper:{}, catcher_switch:{}"
#             "".format(
#                 part_name,
#                 pick_point_2d,
#                 object_with_sucker_img,
#                 pick_point_with_sucker,
#                 bounding_rect_with_gripper,
#                 catcher_switch,
#             )
#         )
#
#         instance = models.SteelWorkpieceCommonInfo.objects.get(part_name=part_name)
#         if len(eval(catcher_switch)) != len(eval(instance.catcher_switch)):
#             raise systatus.AppException(systatus.MAGNETIC_SUCTION_CONFIGURATION_LENGTH_MISMATCH)
#         instance.pick_point_2d = pick_point_2d
#         instance.pick_point_with_sucker = pick_point_with_sucker
#         instance.bounding_rect_with_gripper = bounding_rect_with_gripper
#         instance.catcher_switch = catcher_switch
#         instance.save()
#
#         response_data = {"part_name": part_name, "msg": "修改磁吸配置成功"}
#         return response_data
#
#
# class ManuallyGenerateTask(APIView):
#     """手动上传json图纸及dxf图纸并发送给vision，viz解析"""
#
#     @view_wrapper
#     def post(self, request, *args, **kwargs):
#         """
#         手动上传json图纸，dxf图纸并生成任务
#         @ demo
#         @ url: http://127.0.0.1:8000/steelplate/api/v1/manually-task
#         """
#         current_date = datetime.datetime.now().strftime("%Y-%m-%d")
#         common_info_dir = settings.COMMON_INFO_DIR
#         private_info_dir = settings.PRIVATE_INFO_DIR
#         request_data = request.data["request_data"]
#         json_path = request_data["json_path"]
#         dxf_path = request_data["dxf_path"]
#         thickness = request_data["thickness"]
#         material = request_data["material"]
#
#         if not os.path.exists(json_path):
#             raise systatus.AppException(systatus.DOWNLOAD_FILE_FAILED)
#         if not os.path.exists(dxf_path):
#             raise systatus.AppException(systatus.DOWNLOAD_FILE_FAILED)
#
#         task_id = os.path.basename(json_path).split(".")[0]
#         file_write_path = os.path.join(private_info_dir, current_date, task_id)
#         if not os.path.exists(file_write_path):
#             os.makedirs(file_write_path)
#
#         json_path_in_sys = shutil.copy(json_path, file_write_path)
#         dxf_path_in_sys = shutil.copy(dxf_path, file_write_path)
#         filter_json_path, total_count, active_count = self.filter_big_steel(json_path_in_sys)
#
#         steel_original_info = models.SteelOriginalInfo(
#             task_id=task_id,
#             task_status="wait",
#             total_count=total_count,
#             active_count=active_count,
#             board_thick=thickness,
#             board_type=material,
#             json_path=filter_json_path,
#             dxf_path=dxf_path_in_sys,
#             is_manual_generate=1,
#             created_time=str(datetime.datetime.now()),
#         )
#         steel_original_info.save()
#         msg = {
#             "file_write_path": file_write_path,
#             "filter_json_path": filter_json_path,
#             "json_path": json_path_in_sys,
#             "dxf_path": dxf_path_in_sys,
#             "common_info_dir": common_info_dir,
#         }
#         vision_msg = messages.ServerAdapterMessageTemplate(receiver=("vision", "viz"), task_id=task_id, msg=msg)
#         parse_center.submit_task_to_parse(vision_msg, orientation="left")
#
#         response_msg = {"task_id": task_id, "msg": "接收图纸解析任务成功"}
#         return response_msg
#
#     def filter_big_steel(self, path):
#         """筛选出大件"""
#         with open(path, "r", encoding="utf-8") as f:
#             data = json.loads(f.read())
#             part_list = []
#             total_count = len(data["PartList"])
#             for item in data["PartList"]:
#                 if item["PartSize"] == 3:
#                     part_list.append(item)
#             data["PartList"] = part_list
#             active_count = len(part_list)
#         dir_path = os.path.dirname(path)
#         file_name = "filter" + os.path.basename(path)
#         filter_json_path = os.path.join(dir_path, file_name)
#         with open(filter_json_path, "w+", encoding="utf-8") as f:
#             f.write(json.dumps(data, ensure_ascii=False))
#         return filter_json_path, total_count, active_count
#
#
# class GenerateStrategy(APIView):
#     """任务数据生成策略，提供给客户一些可操作的选项来筛选抓取的零件"""
#
#     @view_wrapper
#     def get(self, request, *args, **kwargs):
#         """
#         获取工位支持的策略
#         :param request:
#         :param args:
#         :param kwargs:
#         :return:
#         """
#         query_params = dict(request.query_params.items())
#         line_id = int(query_params["line_id"])
#         generate_strategy = scheduler_center.query_generate_strategy(line_id)
#         support_generate_strategy = [
#             {"type_strategy": "middle", "description": "中件", "length_strategy": [1300, 3000]},
#             {"type_strategy": "big", "description": "大件", "length_strategy": [3000, 5800]},
#         ]
#         generate_strategy["support_generate_strategy"] = support_generate_strategy
#         return generate_strategy
#
#     @view_wrapper
#     def post(self, request, *args, **kwargs):
#         """
#         设置工位的配置
#         :param request:
#         :param args:
#         :param kwargs:
#         :return:
#         """
#         request_data = request.data["request_data"]
#         view_log.info("工位配置中心, 前端传入的配置数据:{}".format(request_data))
#         line_id = request_data["line_id"]
#         redis_work_station_setting = scheduler_center.query_generate_strategy(line_id)
#         generate_strategy = request_data["generate_strategy"]
#
#         if len(generate_strategy) == 0:
#             raise systatus.AppException(systatus.INSTANCE_FILTER_TYPE_OUT_OF_RANGE)
#         for item in generate_strategy:
#             type_strategy = item["type_strategy"]
#             min_length, max_length = item["length_strategy"]
#             if type_strategy == "middle" and (max_length <= 3000 and min_length > 1300):
#                 continue
#             elif type_strategy == "big" and (max_length <= 5800 and min_length > 3000):
#                 continue
#             else:
#                 raise systatus.AppException(systatus.INSTANCE_SIZE_OUT_OF_RANGE)
#         redis_work_station_setting["generate_strategy"] = generate_strategy
#         scheduler_center.set_generate_strategy(line_id, redis_work_station_setting)
#         response = {"line_id": line_id, "msg": "设置工位配置成功"}
#         return response
#
#
# #
class SaveMaterialId(APIView):
    def post(self, request, *args, **kwargs):
        pass
