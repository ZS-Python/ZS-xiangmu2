from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import db,create_app,models



app =create_app('dev')

# 6, flask_Script和数据库迁移
manage = Manager(app)
Migrate(app,db)

manage.add_command('sql',MigrateCommand)



if __name__ == '__main__':
    print(app.url_map)
    manage.run()
