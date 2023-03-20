from rest_framework.views import APIView
from rest_framework.response import Response
from celery import result
from rest_framework import status
from utils.rediscache import c_cache


class AsyncResult(APIView):
    """
    获取异步任务的结果,
    URL类似于: http://127.0.0.1:8000/asyncresult/api/v1/98a4dfe2-f456-4958-8917-ab7863be4169/
    """
    def get(self, request, *args, **kwargs):
        version = kwargs.get("version")
        task_id = kwargs.get("task_id")
        print("version:{}, task_id:{}".format(version, task_id))
        instance = result.AsyncResult(task_id)
        if instance.ready():
            data = {
                "status": instance.state,
                "result": instance.get()
            }
        else:
            data = {
                'status': instance.state,
                'result': ''
            }
        return Response(data, status=status.HTTP_200_OK)


class AsyncResultV2(APIView):
    """
    获取异步任务的结果,
    URL类似于: http://127.0.0.1:8000/syncresult/api/v1/98a4dfe2-f456-4958-8917-ab7863be4169/
    """
    def get(self, request, *args, **kwargs):
        version = kwargs.get("version")
        task_id = kwargs.get("task_id")
        task_id = "celery-task-meta-{}".format(task_id)
        response = c_cache.conn.get(task_id)
        print(response)
        if response:
            data = {
                # "status": instance.state,
                # "result": instance.get()
            }
        else:
            data = {
                'status': '',
                'result': ''
            }
        return Response(data, status=status.HTTP_200_OK)