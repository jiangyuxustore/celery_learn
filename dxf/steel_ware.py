from django.utils.deprecation import MiddlewareMixin
import time
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.middleware.csrf import CsrfViewMiddleware

class Timeit(MiddlewareMixin):

    def process_request(self, request):
        """
        process_request可以返回两种值, 一种是None, 一种是HttpResponse
        返回None则继续执行下一个中间件的process_request方法
        返回HttpResponse不会执行下一个中间件的process_request方法直接跳转执行process_response方法
        """
        print("执行Timeit类中的process_request")
        # response = Response(
        #     data='User is blocked due to exceeding throttles limit.',
        #     status=403
        # )
        # response.accepted_renderer = JSONRenderer()
        # response.accepted_media_type = "application/json"
        # response.renderer_context = {}
        # response.render()
        # return response
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        process_view可以返回三种值, 一种是None, 一种是HttpResponse, 一种是view_func(request) 执行后的返回值
        返回None则继续执行下一个中间件的process_view方法
        返回HttpResponse不会执行下一个中间件的process_view方法直接跳转执行process_response方法
        返回view_func(request)则继续执行下一个, 但当这种模式运行的时候视图报错, 则不会执行process_exception
        """
        print("执行Timeit类中的process_view")
        start_time = time.time()
        response = view_func(request, view_args, view_kwargs)
        end_time = time.time()
        print("视图函数执行花费时间为:{}s".format(end_time - start_time))
        return response

    def process_exception(self, request, exception):
        print("执行Timeit类中的process_exception")
        return None

    def process_response(self, request, response):
        print("执行Timeit类中的process_response")
        return response


class InfoCatch(MiddlewareMixin):

    def process_request(self, request):
        print("执行InfoCatch类中的process_request")
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        print("执行InfoCatch类中的process_view")
        return None

    def process_exception(self, request, exception):
        print("执行InfoCatch类中的process_exception")
        return None

    def process_response(self, request, response):
        print("执行InfoCatch类中process_response")
        return response