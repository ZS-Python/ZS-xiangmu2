from . import passport_blue
from flask import request,abort,current_app,jsonify,session,json
from info.utils.captcha.captcha import captcha
from info import redis_store,constants,response_code
import re, random,datetime
from info.models import User
from info import db


@passport_blue.route('/exit')
def exit():

    # 清空redis中的session
    try:
        session.pop('user_id')
        session.pop('mobile')
        session.pop('nick_name')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DATAERR, errmsg='退出登陆失败')

    return jsonify(errno=response_code.RET.OK, errmsg='退出登陆成功')


# 登陆
@passport_blue.route('/login',methods=['POST'])
def login():
    # 接收参数
    json_dict = request.json
    mobile = json_dict.get('mobile')
    password = json_dict.get('password')

    if not all([mobile,password]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数不全')
    if not re.match(r'^1[345678][0-9]{9}$',mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机格式错误')

    # 取出数据库中的信息
    try:
        user_info = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='获取信息失败')

    if not user_info:
        return jsonify(errno=response_code.RET.DBERR, errmsg='用户名或者密码错误')

    if not user_info.check_passowrd(password):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='用户名或密码错误')

    # 更新登陆时间
    user_info.last_login = datetime.datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='登陆时间更新失败')

    # 设置状态保持
    session['user_id'] = user_info.id
    session['mobile'] = mobile
    session['nick_name'] = mobile

    return jsonify(errno=response_code.RET.OK, errmsg='登陆成功')



# 输入密码注册账号
@passport_blue.route('/register',methods=['GET','POST'])
def register():
    # 接收参数(手机号,密码,短信验证码)
    json_str = request.data
    json_dict = json.loads(json_str)
    mobile = json_dict.get('mobile')
    password = json_dict.get('password')
    sms_code_client = json_dict.get('sms_code')

    if not all([mobile,password,sms_code]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数不全')

    if not re.match(r'^1[345678][0-9]{9}$',mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机格式错误')
    # 获取服务器端的短信验证码
    try:
        sms_code_server = redis_store.get('SMS:' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='获取短信验证码失败')

    if sms_code_client != sms_code_server:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='短信验证码输入错误')


    # 创建模型对象,并赋值属性

    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    # 密码加密处理(方法在models.py中)
    user.password = password
    # 更新注册时间
    user.last_login = datetime.datetime.now()

    # 存储手机密码到mysql数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='存储注册信息失败')

    # 注册即登陆,保持状态到session
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.mobile

    return jsonify(errno=response_code.RET.OK, errmsg='注册成功')




# 点击获取验证码
@passport_blue.route('/sms_code',methods=['POST'])
def sms_code():
    # 接收手机号和图片验证码和图片uuid
    json_dict = request.json
    mobile = json_dict.get('mobile')
    image_code_client = json_dict.get('image_code')
    imageCodeId = json_dict.get('imageCodeId')

    if not all([mobile,image_code,imageCodeId]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')

    if not re.match(r'^1[345678][0-9]{9}$',mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机格式错误')

    # 从redis数据库取出uuid:验证码
    try:
        image_code_server = redis_store.get('imageCodeId:' + imageCodeId)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='获取服务器端图片验证码失败')

    if image_code_server.lower() != image_code_client:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='图片验证码错误')

    # 生产短信验证码
    sms_code = '%06d' % random.randint(0,999999)
    print(sms_code)

    # 通过云通讯发送验证码

    # 存储短信验证码
    try:
        redis_store.set('SMS:' + mobile, sms_code, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='存储短信验证码失败')

    return jsonify(errno=response_code.RET.OK, errmsg='发送短信验证码成功')



@passport_blue.route('/image_code')
def image_code():

    # 提供图片验证码,并存在redis
    imageCodeId = request.args.get('imageCodeId')

    if not imageCodeId:
        abort(403)

    # 生成图片验证码
    name, text ,image = captcha.generate_captcha()

    # 保存图片验证码
    try:
        redis_store.set('imageCodeId:' + imageCodeId, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    return image


