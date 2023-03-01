# -*- coding: utf-8 -*-
"""
@Auth ： 江宇旭
@Email ：jiang.yuxu@mech-mind.net
@Time ： 2023/2/28 14:19
"""
import pymysql
from dbutils.pooled_db import PooledDB

db_config = {
    "host": '124.70.136.165',
    "port": 3306,
    "user": 'root',
    "passwd": 'Jiangyuxu123...',
    "db": 'dxf'
}


class MysqlConnectionPool(object):
    """mysql connection pool"""
    def __init__(self, database='dxf'):
        """
        连接池初始化
        :param database: str, 连接的数据库名
        """
        self.connection_pool = PooledDB(pymysql, 5, database=database, **db_config)

    def get_connection(self):
        """
        默认情况下创建的connection是可以线程共享的, 设置shareable=False则指定线程独享
        :return:
        """
        return self.connection_pool.connection(shareable=False)


mysql_pool = MysqlConnectionPool()

