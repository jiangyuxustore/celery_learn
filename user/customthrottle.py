"""自定义频率访问控制"""
from rest_framework.throttling import BaseThrottle
import time
from django.core.exceptions import ImproperlyConfigured
from django.core.cache import cache
from rest_framework.settings import api_settings


class VisitThrottle(BaseThrottle):

    cache = cache
    scope = "burst"
    timer = time.time
    cache_format = 'throttle_%(scope)s_%(ident)s'
    THROTTLE_RATES = api_settings.DEFAULT_THROTTLE_RATES

    def __init__(self):
        if not getattr(self, 'rate', None):
            self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)
        self.key = None
        self.history = None
        self.now = None

    def get_rate(self):
        """
        这个方法是通过setting.py中DEFAULT_THROTTLE_RATES, 然后根据设置scope这个key去
        取设置频率, 比如setting.py中, 然后根据scope= "burst", 就可以从字典中拿到这个对应的值
        "DEFAULT_THROTTLE_RATES": {
            "anon": "3/min",
            "burst": "3/min",
            "sustained": "1000/day"
        }
        """
        if not getattr(self, 'scope', None):
            msg = ("You must set either `.scope` or `.rate` for '%s' throttle" %
                   self.__class__.__name__)
            raise ImproperlyConfigured(msg)

        try:
            return self.THROTTLE_RATES[self.scope]
        except KeyError:
            msg = "No default throttle rate set for '%s' scope" % self.scope
            raise ImproperlyConfigured(msg)

    def parse_rate(self, rate):
        """从setting.py中拿到频率后进行字符串的解析, 比如3/min, 就是通过该方法解析的"""
        if rate is None:
            return None, None
        num, period = rate.split('/')
        num_requests = int(num)
        duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]
        return num_requests, duration

    def allow_request(self, request, view):
        """
        allow_request返回True则允许访问, 返回False则不允许访问
        原理就是记录访问者的ip然后记录访问的时间戳, 一分钟内访问超过3次就拒绝继续访问
        """
        if self.rate is None:
            return True

        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        # Drop any requests from the history which have now passed the
        # throttle duration
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return False
        return self.throttle_success()

    def get_cache_key(self, request, view):

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }

    def throttle_success(self):
        """
        Inserts the current request's timestamp along with the key
        into the cache.
        """
        self.history.insert(0, self.now)
        self.cache.set(self.key, self.history, self.duration)
        return True

    def wait(self):
        """提醒用户多少秒后才可以继续访问."""
        if self.history:
            remaining_duration = self.duration - (self.now - self.history[-1])
        else:
            remaining_duration = self.duration

        available_requests = self.num_requests - len(self.history) + 1
        if available_requests <= 0:
            return None

        return remaining_duration / float(available_requests)
