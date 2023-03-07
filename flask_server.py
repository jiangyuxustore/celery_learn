from flask import Flask, send_file
from flask_restful import Resource, Api
import time
import random

app = Flask(__name__)
api = Api(app)


class DownLoad(Resource):
    def get(self):
        seconds = random.randint(1, 10)
        print("模拟文件下载io, 休眠:{}s".format(seconds))
        time.sleep(seconds)
        return send_file('dxf&jsonMap/3210915F8415/3210915F8415.dxf', as_attachment=True)

    def post(self):
        seconds = random.randint(1, 10)
        time.sleep(3)
        res_dict = {'start': 190, 'end': 202}
        return res_dict


api.add_resource(DownLoad, '/download')

if __name__ == '__main__':
    app.run("0.0.0.0", 5000)
