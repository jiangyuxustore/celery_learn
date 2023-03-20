"""
Django settings for dxflearn project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from kombu import Queue, Exchange
from pathlib import Path
# from dxflearn.router import default_queue, topic_queue, quorum_queue

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-slm@76qes+m7nwix4x408=wo@9pu0_9*6#&)wvx-g1-x0od206'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'dxf',
    'user',
    'steelplate',
    'asyncresult',
    'blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dxflearn.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dxflearn.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "dxf",
        "USER": "root",
        "PASSWORD": "Jiangyuxu123...",
        "HOST": "124.70.136.165",
        "PORT": 3306
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =====================================redis session 相关配置 =========================================

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.146.201:8003/0",  # 使用redis 读集群
        "TIMEOUT": 86400,
        "OPTIONS": {
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "REDIS_CLIENT_CLASS": "rediscluster.RedisCluster",  # 使用redis集群时需要设置REDIS_CLIENT_CLASS="rediscluster.RedisCluster"
            # 'CONNECTION_POOL_CLASS': 'rediscluster.connection.ClusterConnectionPool',  # 使用redis集群时需要设置CONNECTION_POOL_CLASS="rediscluster.connection.ClusterConnectionPool"
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
                "retry_on_timeout": True,
                "skip_full_coverage_check": True  # 使用redis集群时需要设置skip_full_coverage_check=True
            },
            # "PASSWORD": "django-insecure-jiangyuxu-learn-django",
            "SOCKET_CONNECT_TIMEOUT": 5,  # 建立socket连接的超时时间
            "SOCKET_TIMEOUT": 5,          # 建立socket连接后的读写的超时时间
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.146.201:8003/0",  # 使用redis 读集群
        "TIMEOUT": 86400,
        "OPTIONS": {
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "REDIS_CLIENT_CLASS": "rediscluster.RedisCluster",
            # 'CONNECTION_POOL_CLASS': 'rediscluster.connection.ClusterConnectionPool',
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
                "retry_on_timeout": True,
                "skip_full_coverage_check": True
            },
            # "PASSWORD": "django-insecure-jiangyuxu-learn-django",
            "SOCKET_CONNECT_TIMEOUT": 5,  # 建立socket连接的超时时间
            "SOCKET_TIMEOUT": 5,          # 建立socket连接后的读写的超时时间
        }
    }
}

# session使用的存储方式
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# 指明使用哪一个库保存session数据
SESSION_CACHE_ALIAS = "session"
# 设置session失效时间,单位为秒
SESSION_COOKIE_AGE = 60*5


# =====================================邮件 相关配置 ===========================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 25
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = '377832421@qq.com'
EMAIL_HOST_PASSWORD = 'msxvsbobaltbbgcf'


# ====================================celery 相关配置 ==========================================

# CELERY_BROKER_URL = 'pyamqp://liying:jiangyuxu@124.70.136.165:5672'   # 使用单机的rabbitmq
# CELERY_RESULT_BACKEND = 'redis://:django-insecure-jiangyuxu-learn-django@124.70.136.165:6379/3' # 使用单机的redis
CELERY_BROKER_URL = 'pyamqp://liying:jiangyuxu@192.168.146.201:8001'    # 使用rabbitmq集群
CELERY_RESULT_BACKEND = 'redis://192.168.146.201:8002/0'                # 使用redis 写集群
CELERY_RESULT_EXPIRES = 3600 * 12  # celery任务结果过期时间
CELERY_TIMEZONE = 'Asia/Shanghai'
# RESULT_BACKEND_TRANSPORT_OPTIONS 是redis断开重连的时间
RESULT_BACKEND_TRANSPORT_OPTIONS = {
    'retry_policy': {
        'timeout': 5.0
    }
}
CELERY_ACKS_LATE = True
CELERYD_PREFETCH_MULTIPLIER = 3  # 设置worker的预取消息数
# # 官网上定义队列都是定义在CELERY_QUEUES中, 但这种设置并不生效,
# CELERY_QUEUES = (
#     Queue("default_queue", exchange=Exchange("default_exchange", type='direct'), routing_key="default",
#           durable=True, auto_delete=True,
#           queue_arguments={'x-queue-type': 'classic'}),
#     Queue("topic_queue", exchange=Exchange("topic_exchange", type="topic"), routing_key="user.#",
#           bindings="user.#", durable=True, auto_delete=True,
#           queue_arguments={'x-max-priority': 10, 'x-queue-type': 'classic', 'x-max-length': 2000000}),
#     Queue("quorum_queue", exchange=Exchange("quorum_exchange", type="topic"), routing_key="blog.#",
#           bindings="blog.#",
#           queue_arguments={
#              'x-queue-type': 'quorum',
#              'x-max-length': 2000000,
#              'x-overflow': 'reject_publish',
#              'x-delivery-limit': 2,
#              "x-queue-lead-locator": "balanced",
#              # "x-dead-letter-exchange": "dead_letter_exchange",
#              # "x-dead-letter-routing-key": "dead_letter_routing_key"
#          })
#
# )

# 设置全局都不忽略task的结果, 也就是要保存task的结果, 类和函数上ignore_result优先级比这个全局的要高
CELERY_IGNORE_RESULT = False

# ================================rest framework 的全局配置 ======================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser"
    ],
    # 设置全局访问控制
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle"
    ],
    # 匿名用户限制访问是
    "DEFAULT_THROTTLE_RATES": {
        "anon": "13/min",    # 设置匿名用户1分钟可以访问3次, redis中的key过期时间是60s
        "burst": "5/min",
        "sustained": "1000/day"
    },
    # 版本控制相关的默认设置
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",  # 默认的版本
    "ALLOWED_VERSIONS": ["v1", "v2"],  # 只允许v1, v2版本, v3版本不在设置中则不允许
    # 表示URL哪个参数表示version, 比如http://127.0.0.1:8000/api/user?version=v1
    "VERSION_PARAM": "version",

    # 分页相关的设置
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100

}
