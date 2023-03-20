from redis import RedisCluster

r = RedisCluster(host='192.168.146.201', port=8002, )

value = r.get("name")
print(value)
