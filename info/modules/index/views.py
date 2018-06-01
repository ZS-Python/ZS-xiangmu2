# 把视图注册到蓝图中
from . import index_blue
from flask import render_template,current_app,session,request,jsonify
from info.models import User,News
from info import constants,response_code


@index_blue.route('/news_list')
def news_list():
    ''' 查询新闻信息,并创建时间倒序显示'''

    # 1, 查询新闻信息,并创建时间倒序显示
    # 接收参数(cid新闻分类,per_page每页多少条,page当前所在页)
    cid = request.args.get('cid', 1)
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)

    # 参数int
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='参数类型有误')

    # 查询新闻
    if cid == 1:
        paginate = News.query.order_by(News.create_time.desc()).paginate(page, per_page, False)
    else:
        paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page, per_page,
                                                                                                         False)

    # 构造响应新闻数据
    news_list = paginate.items  # 模型对象
    total_page = paginate.pages
    current_page = paginate.page

    # 模型对象列表转成字典列表
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    data = {
        'news_dict_list': news_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }

    return jsonify(errno=response_code.RET.OK, errmsg='成功',data = data)


# 主页图标渲染
@index_blue.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')


# 主页渲染
@index_blue.route("/")
def index():
    # 1, 显示注册登陆或者用户名
    # 2, 主页点击排行


    # 1,获取redis状态信息数据
    user_id = session.get('user_id')

    user = ''
    if user_id:
        try:
            # 获取里面的手机号/用户名
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 2, 主页点击排行
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)


    content = {
        'user': user,
        'news_clicks': news_clicks,

    }

    return render_template('news/index.html',content = content)
