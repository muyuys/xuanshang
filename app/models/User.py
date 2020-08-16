from app import db
from datetime import datetime
import json
from .User_Task import User_Task




class User(db.Model):
    __tablename__ = "User"
    __table_args__ = {
        "mysql_charset": "utf8"
    }

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.Enum('保密', '男神', '女神'), default="保密", nullable=False)
    password = db.Column(db.String(20), nullable=False)

    property = db.Column(db.DECIMAL, default=0.0, nullable=False)
    # DECIMAL定点类型，是专门为了解决浮点类型精度丢失的问题的，一般作用于金钱类型
    head_portrait = db.Column(db.LargeBinary)
    tasknum = db.Column(db.Integer, default=0)  # 已接受任务数
    create_at = db.Column(db.DateTime, default=datetime.now())

    tasks = db.relationship('Task', backref=db.backref('User',lazy='dynamic'), secondary=User_Task)

    def __init__(self, username, email, gender, password):
        self.username = username
        self.email = email
        self.gender = gender
        self.password = password

    def add(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self.id
        except Exception as e:
            db.session.rollback()
            return e

    def __repr__(self):
        return '<User: %r ID: %r>' % (self.username, self.id)


    def accept(self, task):
        self.tasks.append(task)
        # self.tasknum += 1  tasknum是NoneType,需要换个方式修改数据
        self.add()

    def register(self):
        res = {}
        res['id']=None
        if db.session.query(User).filter_by(username=self.username).count() != 0:
            res['result'] = 112
        elif db.session.query(User).filter_by(email=self.email).count() != 0:
            res['result'] = 113
        else:           
            res['id']=self.add()
            res['result'] = 111
        return json.dumps(res)

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
