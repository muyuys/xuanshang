from app import db
import json


class User_Task(db.Model):
    
    
    __tablename__ = 'user_task'  # 中间表
    __table_args__ = {
        "mysql_charset": "utf8"
    }

    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('Task.id'), primary_key=True)
    status = db.Column(db.Boolean, default = False)
    create_at = db.Column(db.DateTime, default = datetime.now())

    def __init__(self,user_id,task_id):
        self.user_id = user_id
        self.task_id = task_id
    
    def get_status(self):
        return {"status":self.status}
  
    def add(self):
        try:
            db.session.add(self)
            db.session.commit()
            return  self.id
        except Exception as e:
            db.session.rollback()
            return  e
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}