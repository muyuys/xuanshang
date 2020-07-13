#-*- coding:utf-8 -*-
import base64
import os
import numpy as np
import json
import gzip

from flask import Flask, request,jsonify,Response
from flask_sqlalchemy import SQLAlchemy
from flask_compress import Compress
from flask_cors import *
from sqlalchemy import or_
from sqlalchemy.sql.expression import func
from datetime import datetime


app = Flask(__name__)
CORS(app,supports_credentials=True)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@#$%Yzndmm0902@localhost/zongshe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['COMPRESS_MIN_SIZE'] = 1024
app.config['COMPRESS_MINETYPES'] = ['application/json']

db = SQLAlchemy(app)

def send_img(filename):
    img=""
    for line in open(filename,"r"):
        img+=line
    return img

def to_json(Obj):
    dict = Obj.__dict__
    if "_sa_instance_state" in dict:
        del dict["_sa_instance_state"]
    return dict

# def to_json(r):
#     res={}
#     for c in r.__table__.columns:
#         res[c.name]=str(getattr(r,c.name))
#     return res


user_label = db.Table(
    'user_label',  # 中间表
    db.Column('user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True),
    db.Column('label_id', db.Integer, db.ForeignKey('Label.id'), primary_key=True)
)


class Label(db.Model):
    __tablename__ = "Label"
    __table_args__ = {
        "mysql_charset": "utf8"
    }
    id = db.Column(db.Integer,unique=True,nullable =False,primary_key=True)#同时也是标签图像ID
    name = db.Column(db.String(15),unique=True,nullable =False)

    def __init__(self,id,name):
        self.id = id
        self.name = name
    
    def add(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self.id
        except Exception as e:
            db.session.rollback()
            return e
    


    
    def __repr__(self):
        return '<Label: %r ID: %r>' % (self.name, self.id)




class User(db.Model):
    __tablename__ = "User"
    __table_args__ = {
        "mysql_charset": "utf8"
    }

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    nickname = db.Column(db.String(50), unique=True, nullable=False)
    university = db.Column(db.String(50),nullable=False)
    zodiac = db.Column(db.String(20))#星座,可以用枚举
    email = db.Column(db.String(120), unique=True)
    gender = db.Column(db.Enum('保密', '男神', '女神'), default="保密", nullable=False)
    password = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(50))
    imgbytes = db.Column(db.Text) # 存储图片的地址
    
    labels = db.relationship('Label',secondary= user_label,backref = db.backref('User'))
    

    def __init__(self, nickname, email, university,zodiac,location,gender, password,imgbytes):
        self.nickname = nickname
        self.email = email
        self.university = university
        self.zodiac = zodiac
        self.location = location
        self.gender = gender
        self.password = password
        self.imgbytes = imgbytes

    def add(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self.id
        except Exception as e:
            db.session.rollback()
            return e

    def __repr__(self):
        return '<User: %r ID: %r>' % (self.nickname, self.id)

    def save_img(self,imgbytes):
        self.imgbytes="./zongshe2/"+self.nickname+".txt" # 图片base64编码路径
        # print(self.imgbytes)
        fp = open(self.imgbytes,"w")
        fp.write(imgbytes)
        fp.close() 

    def register(self):
        res = {}
        if len(db.session.query(User).filter_by(nickname=self.nickname).all()) != 0:          
            # 昵称(用户名)已存在
            res['result'] = 1
        elif len(db.session.query(User).filter_by(email=self.email).all()) != 0:
            # 邮箱已存在
            res['result'] = 2
        else:
            print('注册成功')
            res['result'] = 0
            self.add()
        return json.dumps(res)

    def login(self):
        res = {}
        data = db.session.query(User).filter_by(nickname=self.nickname, password=self.password).all()
        if len(data) == 1:
            # for r in data:
                # row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}#结果集转字典用于转换为json
                # res['UID'] = row2dict(r)['id']
            # 登录成功
            res['result']= 0
        else :
            # 登录失败
            res['result']= -1
        return json.dumps(res)

    def match(self):
        res=[]
        data = db.session.query(User).filter(
            User.nickname!=self.nickname,or_(User.university==self.university,User.location==self.location)).\
            order_by(func.random()).limit(3).all()
        i=0
        for r in data:
            
            labels = r.labels
            temp=[]
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            for label in labels:
                temp.append(row2dict(label))
            res.append(to_json(r))
            res[i]['labels']=temp
            i+=1        
            
        for r in res:
            r['imgbytes']=send_img(r['imgbytes'])
            del r['gender']
            del r['password']
            del r['id']
            del r['email']

        return json.dumps(res,ensure_ascii=False)


    def modify(self):
        res={}
        # 有问题如果nickname和email同时被修改,那么就找不到对应的数据
        # 应使用id或者提供未被修改之前的nickname或email
        data = db.session.query(User).filter(or_(User.nickname==self.nickname, User.email==self.email)).first()
        if data==None :
            res['result'] = -2
        else :
            data.nickname = self.nickname
            data.email = self.email
            data.university = self.university
            data.zodiac = self.zodiac
            data.location = self.location
            data.gender = self.gender
            data.password = self.password
            data.imgbytes = self.imgbytes
        
        if(not db.session.commit()):
            # 修改成功
            res['result']= 0
        else :
            # 修改失败
            res['result']= -1
        return json.dumps(res)

    def choice_label(self,label:Label):      
        res={}
        try:
            self.labels.append(label)
            db.session.commit()
            res['result']=self.id
            return json.dumps(res)
        except Exception as e:
            db.session.rollback()
            print(e)
            res['result']='failed'
            return json.dumps(res)


@app.route('/register',methods=['POST','GET'])

def register():
    if request.method == 'POST':
        data = request.get_data()
        json_re = json.loads(data)
        nickname = json_re['nickname']
        email = json_re['email']
        university = json_re['university']
        zodiac = json_re['zodiac']
        location = json_re['location']
        gender = json_re['gender']
        password = json_re['password']
        
        imgbytes = json_re['imgbytes']
        
        user = User(nickname,email,university,zodiac,location,gender,password,None)
        user.save_img(imgbytes)
        
    return user.register()

@app.route('/login',methods=['POST','GET'])

def login():
    if request.method=='POST':
        data = request.get_data()
        json_re = json.loads(data)
        nickname = json_re['nickname']
        password = json_re['password']

        user = User(nickname,None,None,None,None,'保密',password,None)

        return user.login()


@app.route('/modify',methods=['POST','GET'])

def modify():
    if request.method=='POST':       
        data = request.get_data()
        json_re = json.loads(data)
        nickname = json_re['nickname']
        email = json_re['email']
        university = json_re['university']
        zodiac = json_re['zodiac']
        location = json_re['location']
        gender = json_re['gender']
        password = json_re['password']
        imgbytes = json_re['imgbytes']
        
        user = User(nickname,email,university,zodiac,location,gender,password,imgbytes)
        
        user.save_img(imgbytes)
        return user.modify()	

@app.route('/upload',methods=['POST','GET'])

def upload():
    if request.method=='POST':
        data = request.get_data()     
        #json_re = json.loads(data)
        #imgstring = json_re['imgbytes']
        #imgdata = base64.b64decode(imgstring)
        print(data)
        res={}
        #res['img']=imgdata
        res['result']= 1
        return json.dumps(res)

@app.route('/match',methods=['POST','GET'])

def match():
    if request.method=='POST':
        data = request.get_data()
        json_re=json.loads(data,encoding="UTF-8")
        nickname = json_re['nickname']
    
        user = db.session.query(User).filter_by(nickname=nickname).first()
        # json_str = str(user.match())
        # json_bytes = bytes(json_str, 'utf8')
        # res = gzip.compress(json_bytes, 9)
        # print(type(res))
        
        # return res
        return user.match()
    return {}

@app.route('/choice_label',methods=['POST','GET'])

def choice_label():
    if request.method=='POST':
        data = request.get_data()
        json_re=json.loads(data,encoding="UTF-8")
        nickname = json_re['nickname']
        label_id = json_re['label_id']
        user = db.session.query(User).filter_by(nickname=nickname).first()
           
        label = db.session.query(Label).filter_by(id=label_id).first()
        print("开始选标签")   
        return user.choice_label(label)
    return {}




if  __name__  ==  '__main__':
    app.run(host='0.0.0.0', port=5000, debug = True)




