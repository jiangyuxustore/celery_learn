from rediscluster import RedisCluster


url = "redis://192.168.146.201:8003/0"


class CustomRedisCluster(object):

    def __init__(self, url):
        self.conn = RedisCluster.from_url(url)

    # def get(self, key):
    #     pass


c_cache = CustomRedisCluster(url)
