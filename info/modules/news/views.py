from . import news_blue
from flask import render_template,current_app,abort,session
from info.models import News,User
from info import constants,db


@news_blue.route('/detail/<int:news_id>')
def news_detail(news_id):
    '''根据点击的新闻的id获取其对应的详情页面'''
    # 1, 从redis获取用户登陆信息,直接取user_id
    user_id = session.get('user_id')

    user = None
    # 判断是否信息存在,存在则显示该用户名
    if user_id:
        try:
            user = User.query.get(user_id)  # user是通过user_id创建的指定对象
        except Exception as e:
            current_app.logger.error(e)

    # 2, 显示点击排行
    # 查询新闻数据,根据clicks的点击量进行倒序排序
    # news_clicks = [News1,News2,News3,News4,News5,News6,],每个模型对象
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        abort(404)


    # 点击量加1
    news.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)

    # 判断是否收藏true为收藏, false为未收藏
    is_collected = False
    if not is_collected:
        if user:
            if news in user.collection_news:  # user.collection_news表示该用户收藏的所有新闻,(用户表的外键)
                is_collected = True


    context = {
        'user':user,
        'news_clicks': news_clicks,
        'news': news.to_dict(),
        'is_collected': is_collected
    }

    return render_template('news/detail.html',context = context)