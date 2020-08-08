import base64
import json
import os

from ..base import base
from .. import db
from ..models import User,Task,Comment

from sqlalchemy import or_
from sqlalchemy.sql.expression import func

row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}

@base.route('/home',methods=['POST','GET'])

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


@base.route('/register',methods=['POST','GET'])

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


@base.route('/login',methods=['POST','GET'])

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

@base.route('/upload',methods=['POST','GET'])

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

@base.route('/task',methods=['POST','GET'])

def task():
    res = {}
    data = request.get_data()
    json_re = json.loads(data)
    tid = json_re['TID']
    uid = json_re['UID']

    task = db.session.query(Task).filter_by(id=tid).first()
    temp = task.to_dict()

    if request.method=='POST':
        res['TID'] = temp['TID']
        res['UID'] = uid 
        
    elif request.method=='GET':
        if task != None:
            res['TaskName']=temp['task_name']
            res['TaskTargetNumber']=temp['acceptable_number']
            res['TaskGottenNumber']=db.session.query(user_task).filter_by(id=tid).count()
            res['Initiator']=temp['initiator']
            res['TaskPayback']=temp['reward']
            res['TaskComments']=[]
            comments = db.session.query(Comment).filter_by(tid=tid).limit(20)
            # 这里需要修改成如何在显示了20个后继续显示20个(分页)
            
            for r in comments:
                temp={}
                temp['UID']=r.to_dict()['uid']
                temp['Comment']=r.to_dict()['comment']
                res['TaskComments'].append(temp)
    return json.dumps(res)

@base.route('/my_tasks',methods=['POST','GET'])

def my_tasks():
    res = {}
    data = request.get_data()
    json_re = json.loads(data)
    uid = json_re['UID']

    user = db.session.query(User).filter_by(id=uid).first()
    
    tasks = user.tasks
    res['Length'] = len(tasks)

    if request.method=='POST':
        res['UID'] = uid 
        
    elif request.method=='GET':
        res['Task']=[]
        if len(tasks) != 0:
            for task in tasks:
                temp = {}
                
                temp['TID'] = task.id
                temp['TaskName'] = task.task_name
                temp['TaskInfo'] = task.introduction
                temp['TaskPayback'] = task.reward
                temp['TaskImage'] = task.img
                temp['Initiator'] = task.initiator
                
                res['Task'].append(temp)
            
            # 这里需要修改成如何在显示了20个后继续显示20个(分页)
    
    return json.dumps(res)


@base.route('/accept_or_abandon_task',methods=['POST','GET'])

def aatask():
    res = {}
    data = request.get_data()
    json_re = json.loads(data)
    uid = json_re['UID']
    tid = json_re['TID']

    task = Task.query.filter(id==tid).first()
    user = User.query.filter(id==uid).first()
    user.tasks.append(task)

    result = user.add()
    if request.method=='POST':
        res['UID']=uid
        res['TID']=tid
        if result==uid:
            res['StatuesCode'] = 111 # 成功
    
    elif request.method=='GET':
        res['ResponseCode']=Response.status
