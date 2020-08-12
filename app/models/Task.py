from app import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = "Task"
    __table_args__ = {
        "mysql_charset": "utf8"
    }

    id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    task_name = db.Column(db.String(50),unique = False)
    introduction =  db.Column(db.Text)
    task_type =  db.Column(db.Enum('daily','study','sports','entertainment'),default = 'daily',nullable = False)# 任务类型
    task_judge_type = db.Column(db.Enum('Personal','GPS','AI'),default = 'Personal',nullable = False)   # 任务判定方式
    acceptable_num =  db.Column(db.Integer,nullable = False)
    img = db.Column(db.String(100),default = '')
    reward = db.Column(db.Integer, default = 0)  # 奖赏
    praise = db.Column(db.Integer, default = 0)  # 点赞数
    create_at = db.Column(db.DateTime,default =  datetime.now())
    initiator =  db.Column(db.Integer,db.ForeignKey('User.id')) # 发布者
    
     
    def __init__(self, task_name,task_type,acceptable_num):
        self.task_name = task_name
        self.task_type = task_type
        self.acceptable_num = acceptable_num     

    def add(self):
        try:
            db.session.add(self)
            db.session.commit()
            return  self.id

        except Exception as e:
            db.session.rollback()
            return  e

    def __repr__(self):
        return  '<Task: %r>' %(self.name)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
