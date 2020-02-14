# HTTP接口(通信协议)

**说明：在本文档里列出的http请求均省略了域名，例如，服务器的域名为[mxb360.top](http://mxb360.top),文档给的http请求为[/eregec/api/index](http://mxb360.top/eregec/api/index)，则完整的http请求应该是[http://mxb360.top/eregec/api/index](http://mxb360.top/eregec/api/index)**

### 协议介绍
客户端与服务器的通信协议是http协议。  
客户端向服务器发送一个http请求，服务器返回给客服端一个json格式的应答。  
  
例如：  
http请求：[/eregec/api/index](http://mxb360.top/eregec/api/index)，服务器应答：  
```json
{
    "data":
    {
    },
    "message": "OK",
    "code": 0
}
```
  
对于所有的json格式的应答，json的内容和上面是相似的。  
即返回的每一个json数据都包含`"data"`, `"message"`, `"code"`。  
* `"data"`: json对象，返回的具体数据
* `"message"`: 字符串，返回状态信息描述，如果操作成功，值为"OK"，如果操作失败，为错误类型名
* `"code"`: 整数，返回状态码，如果操作成功，值为0，如果操作失败，为错误状态码，大于0


### 返回状态信息
从json数据包含的内容看，如返回状态信息有关的内容是`"message"`和`"code"`  
下面给出可能的状态码和对应的状态信息名：  

| 状态码("code")  | 状态信息("message")           |   说明
|----------------|------------------------------|-------------------
| 0              | "OK"                         | 操作成功
| 1              | "HttpArgumentError"          | Http请求参数错误，一般是参数不够
| 2              | "UserLoginError"             | 登录错误，如用户名和密码不正确
| 3              | "UserIdError"                | 用户ID错误，如指定的用户不存在
| 4              | "PlatformNotConnectError"    | 平台不在线，如硬件平台没有连接服务器
| 5              | "DataFaildError"             | 数据传送错误
| 6              | "CommandFaildError"          | 命令执行失败

如果操作出错（即`"code"`不为0），`"data"`里包含的json数据只有`"details"`，是具体的错误描述。  
如登录密码错误时返回的json结果：
```json
{
    "data": 
    {
        "details": "password error"
    }, 
    "message": "UserLoginError", 
    "code": 2
}
```

### 请求参数

参数传递同时支持GET请求和POST请求，因此你可以根据情况使用GET或者POST，甚至，可以混用。  
服务器优先使用POST参数。  
为了安全，建议使用POST请求传参。


### 具体API

**说明：对于任何一个请求，如果操作失败，返回错误状态信息，操作成功，返回的结果全在`"data"`里，因此，在接下来的API介绍里，对于返回值的说明只包含在操作成功时返回的`"data"`内的内容。**
  
  
##### 1. 测试API
  测试API  | 　　 
-----------|-----------------------------------------------------------
  请求     | [/eregec/api/index](http://mxb360.top/eregec/api/index)  
  功能     | 测试使用，可以用于测试服务器是否正常工作  
  参数     | 无
  返回     | 空
操作成功后完整的返回例子：
```json
{
    "data":
    {
    },
    "message": "OK",
    "code": 0
}
```

##### 2. 用户登录
  用户登录  | 　　 
-----------|-----------------------------------------------------------
  请求     | [/eregec/api/login](http://mxb360.top/eregec/api/login)  
  功能     | 用户登录，并获取用户ID
  参数     | `name     ` 用户名(必需参数)
  参数     | `password ` 密码(必需参数)
  返回     | `"userid" ` 登录成功后的用户ID(字符串)
操作成功后完整的返回例子：
```json
{
    "data":
    {
        "userid": "100001"
    },
    "message": "OK",
    "code": 0
}
```

##### 3. 平台数据请求
平台数据请求| 　　 
-----------|-----------------------------------------------------------
  请求     | [/eregec/api/platform-data](http://mxb360.top/eregec/api/platform)  
  功能     | 返回用户平台的实时数据
  参数     | `userid        ` 用户ID(必需参数)
  返回     | 数据名称：数据值...
操作成功后完整的返回例子：
```json
{
    "data":
    {
        "temperature": 37.5,
        "humidity": 25.2
    },
    "message": "OK",
    "code": 0
}
```

##### 4. 平台信息获取
平台信息获取| 　　 
-----------|-----------------------------------------------------------
  请求     | [/eregec/api/platform-info](http://mxb360.top/eregec/api/platform)  
  功能     | 返回用户平台的实时数据
  参数     | `userid  ` 用户ID(必需参数)
  返回     | `"name"  ` 平台名称
  返回     | `"id"  `   平台ID
操作成功后完整的返回例子：
```json
{
    "data":
    {
        "name": "RaspberryPi",
        "id": "eregecuserplatform"
    },
    "message": "OK",
    "code": 0
}
```

##### 5. 向平台发送命令
向平台发送命令 | 　　 
--------------|-----------------------------------------------------------
    请求      | [/eregec/api/cmd](http://mxb360.top/eregec/api/cmd)  
    功能      | 向平台发送命令
    参数      | `userid     ` 用户ID(必需参数)
    参数      | `string     ` 具体命令(必需参数)
    返回      | 空
注：如果命令发送失败，或者平台执行命令失败，都会返回错误状态信息。  
操作成功后完整的返回例子：
```json
{
    "data":
     {
     },
    "message": "OK",
    "code": 0
}
```

##### 6. 用户登出
用户登出   | 　　 
-----------|-----------------------------------------------------------
  请求     | [/eregec/api/logout](http://mxb360.top/eregec/api/logout)  
  功能     | 用户平台的实时数据
  参数     | `userid     ` 用户ID(必需参数)
  返回     | 空
操作成功后完整的返回例子：
```json
{
    "data":
     {
     },
    "message": "OK",
    "code": 0
}
```
