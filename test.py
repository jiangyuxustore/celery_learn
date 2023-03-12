import time

import requests
import json


header = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}


response = requests.post("http://127.0.0.1:8000/blog/api/v1/async-add/", data=json.dumps({"x": 10, "y": 2}), headers=header)
content = json.loads(response.content)
terminate_task_list = [content["class_instance_id"], content["function_instance_id"], content["function_instance_v2_id"]]
time.sleep(3)
print("terminate task list:{}".format(terminate_task_list))
response1 = requests.post("http://127.0.0.1:8000/blog/api/v1/terminate-task/", data=json.dumps({"task_id": terminate_task_list}), headers=header)
print(json.loads(response1.content))


response = requests.post("http://127.0.0.1:8000/blog/api/v1/async-add/", data=json.dumps({"x": 10, "y": 2}), headers=header)
content = json.loads(response.content)
remove_task_list = [content["class_instance_id"], content["function_instance_id"], content["function_instance_v2_id"]]
print("remove task list:{}".format(remove_task_list))
response1 = requests.post("http://127.0.0.1:8000/blog/api/v1/remove-task/", data=json.dumps({"task_id": remove_task_list}), headers=header)
print(json.loads(response1.content))
