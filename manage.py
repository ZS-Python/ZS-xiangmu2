from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import db
from info import create_app


app =create_app('unit')

# 6, flask_Script和数据库迁移
manage = Manager(app)
Migrate(app,db)
manage.add_command('sql',MigrateCommand)



@app.route("/")
def index():

    # result = redis_store.set('name', '123')
    # print(result)

    # 测试session是否存入redis
    from flask import session
    session['name'] = 'zs'

    return "index"


if __name__ == '__main__':
    manage.run()