服务器各个路由上传(post)和返回(get)的json格式(使用实例)

1. `/home`

- post

```json
{"UID":"xxx"}
```
- get

```json
{
  "userHeadBitmap": "bitmap",
  "userMoney": 332,
  "firstTask": 1,
  "endTask": 5,
  "Tasks": [
    {
      "TID": 1,
      "TaskName": "任务接受测试",
      "TaskInfo": "非常简单的测试任务",
      "TaskCategory": "study",
      "TaskJudgeType": "None",
      "TaskPayback": 20,
      "TaskImg": "bitmap",
      "Initiator": 1,
      "Praise": 332,
      "TaskDate": 20200801164521
      "TaskState": 0  //0为未接受，1为已接受，2为已完成
    },
    {
      "TID": 2,
      "TaskName": "跑步一公里",
      "TaskInfo": "非常简单的测试任务",
      "TaskCategory": "sports",
      "TaskJudgeType": "GPS",
      "TaskPayback": 20,
      "TaskImg": "bitmap",
      "Initiator": 1,
      "Praise": 332,
      "TaskDate": 20200801164522,
      "TaskState": 2
    },
    {
      "TID": 3,
      "TaskName": "图像测试",
      "TaskInfo": "非常简单的测试任务",
      "TaskCategory": "entertainment",
      "TaskJudgeType": "AI",
      "TaskPayback": 20,
      "TaskImg": "bitmap",
      "Initiator": 1,
      "Praise": 666,
      "TaskDate": 20200801164523,
      "TaskState": 1

    },
    {
      "TaskName": "个人向测试",
      "TaskInfo": "非常简单的测试任务",
      "TaskCategory": "entertainment",
      "TaskJudgeType": "Personal",
      "TaskPayback": 20,
      "TaskImg": "bitmap",
      "Initiator": 1,
      "Praise": 3212,
      "TaskDate": 20200801164525,
      "TaskState": 0
    }
  ]

}

```

2. `/login`

- post

```json
{
    "username":"张三",
    "password":"123456"
}
```

- get

```json
{
    "UID":1,
    "Result":111
}
```

3. `/register`

- post

```json
{
    "username":"xxx",
    "email":"xxx@example.com",
    "password":"12345"
    
}
```

- get

```json
{
    "Result":111
}
```



4. `/task`

- post

```json
{
    "UID":1,
    "TID":1
}
```

- get

```json
{
    "TaskName":"做一道菜",
    "TaskTargetNumber":10,
    "TaskGottenNumber":2,
    "TaskPayback":10,
    "Initiator":1,
    "TaskComments":[
        {
            "UID":1,
            "Comment":"挺好"
        },
        {
            "UID":2,
            "Comment":"不错"
        }
    ]
}
```

5. `/my_tasks`

- post

```json
{
    "UID":1,
    "Length":2
}
```

- get

```json
{
    "Length": 2,
    "Task":[
        {
            "TID":1,
            "TaskName":"做一道菜",
            "TaskInfo":"",
            "TaskPayback":10,
            "TaskImage":"",
            "Initiator":1
        },
        {
            "TID":2,
            "TaskName":"跑步一公里",
            "TaskInfo":"",
            "TaskPayback":10,
            "TaskImage":"",
            "Initiator":1
        }
    ]
}
```

6. `/accept_or_abandon_task`

- post

```json
{
    "UID":1,
    "TID":1,
    "StatuesCode":111
}
```

- get

```json
{
    "ResponseCode":111
}
```

7. `/finished_tasks`

- post

```json
{
    "UID":1,
    "Length":1
}
```

- get

```json
{
    "Length": 1,
    "Task":[
        {
            "TID":1,
            "TaskName":"做一道菜",
            "TaskInfo":"",
            "TaskPayback":10,
            "TaskImage":"",
            "Initiator":1
        }
    ],
    "ResponseCode":111
}
```

8. `/make_comments`

- get
- post