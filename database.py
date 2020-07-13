import base64
import os
import numpy as np
import json
import cv2

from flask import Flask, request,jsonify,Response
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.sql.expression import func
from datetime import datetime


row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@#$%Yzndmm0902@localhost/xuanshang'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


user_task = db.Table(
    'user_task',  # 中间表
    db.Column('user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True),
    db.Column('task_id', db.Integer, db.ForeignKey('Task.id'), primary_key=True)
)


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

    tasks = db.relationship('Task', backref='User', secondary=user_task)

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

class Task(db.Model):
    __tablename__="Task"
    __table_args__ = {
        "mysql_charset": "utf8"
    }

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    task_name =db.Column(db.String(50),unique=False)
    introduction=db.Column(db.Text)
    task_type=db.Column(db.Enum('日常','学习','运动','挑战'),default='日常',nullable=False)
    acceptable_num=db.Column(db.Integer,nullable=False)
    img = db.Column(db.LargeBinary)
    reward = db.Column(db.Integer)  
    create_at = db.Column(db.DateTime,default=datetime.now())
    receiver=db.Column(db.Integer,db.ForeignKey('User.id'))
     
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


@app.route('/home',methods=['POST','GET'])

def home():
    res={}
    data = request.get_data()
    json_re = json.loads(data)
    uid = json_re['uid']
    user = db.session.query(User).filter_by(id=uid).first()
    temp=user.to_dict()
    if request.method=='POST':
        res['UID']=temp['id']
    elif request.method=='GET':
        tasks=db.session.query(Task.id,Task.task_name,Task.introduction,Task.img,Task.receiver).\
            filter(Task.acceptable_num!=0).order_by(func.random()).limit(5).all()
        if len(tasks)!=0:
            res['Length']=len(tasks)
            res['tasks']=[]
            for r in tasks:
                temp=['TID','taskName','taskInfo','taskPayback','taskImage','OUID']
                res['tasks'].append(dict(zip(temp,r)))
    return json.dumps(res)


@app.route('/register',methods=['POST','GET'])

def register():
    data = request.get_data()
    json_re = json.loads(data)
    username = json_re['username']
    email = json_re['email']
    password = json_re['pwd']
    user = User(username, email, '保密',password)
    reg_res=user.register()
    if request.method == 'POST':
        res['Username']=username
        res['Password']=password
        res['email']=email
    elif request.method =='GET':
        res['UID']=reg_res['id']
        res['Result']=reg_res['result']
        res['ResponseCode']=Response.status
    return json.dumps(res)


@app.route('/login',methods=['POST','GET'])

def login():
    res={}
    data = request.get_data()
    json_re = json.loads(data)
    username = json_re['username']
    password = json_re['pwd']
    user = db.session.query(User).filter_by(username=username).first()
    temp = user.to_dict()
    
    if request.method=='POST':
        res['Username']=temp['username']
        res['Password']=temp['password'] 
        
    elif request.method=='GET':
        if user != None:
            res['UID']=temp['id']
            if temp['password']==password:
                res['ResponseCode']=111
            else:
                res['ResponseCode']=113
        else:
            res['ResponseCode']=112

    return json.dumps(res)

@app.route('/upload',methods=['POST','GET'])

def upload():
    if request.method=='POST':
        data = request.get_data()     
        #json_re = json.loads(data)
        #imgstring = json_re['imgBytes']
        #imgdata = base64.b64decode(imgstring)
        print(data)
        res={}
        #res['img']=imgdata
        res['result']='succeed'
        return json.dumps(res)

@app.route('/img_flip', methods=["POST"])
def process_img():
    # 接收前端传来的图片  image定义上传图片的key
    upload_img = request.files['image']
    print(type(upload_img), upload_img)
    # <class 'werkzeug.datastructures.FileStorage'> <FileStorage: 'phone.jpg' ('image/jpeg')>

    # 获取到图片的名字
    img_name = upload_img.filename

    # 把前端上传的图片保存到后端
    upload_img.save(os.path.join('./', upload_img.filename))

    # 对后端保存的图片进行镜像处理
    img_path = os.path.join('./', upload_img.filename)
    print('path', img_path)
    img = cv2.imread(img_path)
    img_flip = cv2.flip(img, 0)
    cv2.imwrite(os.path.join('./', 'res_' + upload_img.filename), img_flip)

    # 把图片读成二进制，返回到前端
    image = open(os.path.join('./', 'res_' + upload_img.filename), mode='rb')
    response = Response(image, mimetype="image/jpeg")
    return response

        

if  __name__  ==  '__main__':
    app.run(host='0.0.0.0', port=5000, debug = True)


