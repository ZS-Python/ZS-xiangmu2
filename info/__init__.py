from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from redis import StrictRedis
from config import configs
from logging.handlers import RotatingFileHandler
import logging


def level_log(level):
    # 设置日志的记录等级
    logging.basicConfig(level= level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)



# 2, 连接mysql数据库
db = SQLAlchemy()


def create_app(config_name):

    # 调用日志函数
    level_log(configs[config_name].LEVEL_LOG)

    app = Flask(__name__)

    app.config.from_object(configs[config_name])

    db.init_app(app)

    # 3, 连接redis数据库
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST,port=configs[config_name].REDIS_PORT)

    # 4, 开启CSRF保护,这里的保护只做校验,如果是form表单里的和cookie里的csrf_token需要我们自己设置
    CSRFProtect(app)

    # 5, 配置flask_session, 将seesion中的数据保存到Redis数据库中
    Session(app)

    return app
