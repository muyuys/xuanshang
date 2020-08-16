from app import db
from datetime import datetime

class Comment(db.Model):
    __tablename__="Comment"
    __table_args__ = {
        "mysql_charset":"utf8"
    }

    uid = db.Column(db.Integer,db.ForeignKey('User.id'),primary_key=True)
    tid = db.Column(db.Integer,db.ForeignKey('Task.id'),primary_key=True)
    comment = db.Column(db.String(300))
    praise = db.Column(db.Integer,default = 0)
    create_at = db.Column(db.DateTime,default = datetime.now())

    def __init__(self,uid,tid,comment):
        self.uid=uid
        self.tid=tid
        self.comment=comment
    
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