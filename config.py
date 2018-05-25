from redis import StrictRedis
import logging



# 1, 加载配置文件config
class Config():
    # 1, 设置秘钥
    SECRET_KEY = 's55d65ds4f56f56sf5d6sf56s65s'

    # 开启调试
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://root:123@127.0.0.1:3306/new_informations'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = '6379'

    # 配置flask_session, 将seesion中的数据保存到Redis数据库中
    #2, 指定存到redis中
    SESSION_TYPE = 'redis'
    #3, 告诉session redis的位置
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    #4, 是否将session加密签名后存入
    SESSION_USE_SIGNER = True
    #5, 当SESSION_PERMANENT默认为True, 设置session有效期有效
    PERMANENT_SESSION_LIFETIME = 60*60*24 # 一天



# 不同环境下需要不同的配置
class DevelopmentConfig(Config):
    LEVEL_LOG = logging.DEBUG

class ProductConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123@127.0.0.1:3306/new_informations_info'
    LEVEL_LOG = logging.ERROR

class UnittestConfig(Config):
    LEVEL_LOG = logging.DEBUG
    TESTTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123@127.0.0.1:3306/new_informations_test'

# 准备工厂数据
configs = {
    'dev':DevelopmentConfig,
    'pro':ProductConfig,
    'unit':UnittestConfig
}