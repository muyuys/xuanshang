import os
from app import create_app,db
from app.models import User,Task,Comment
from flask import g
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

with app.app_context():
    g.contextPath = ''

def make_shell_context():
    return dict(app=app, db=db, User=User,Task=Task,Comment=Comment)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def myprint():
    print('hello world')


if __name__ == '__main__':
    manager.run()