# Python语言接口

### 介绍
为了方便客户端的开发，本项目提供了对客户端的连接协议做了一个基于Python的封装，屏蔽了客户端与服务器之间的连接协议。(封装服务器的HTTP协议)  
提供本代码的目的是方便用户使用Python语言快速的开发本服务器的客户端。

### 代码
此Python客户端API代码位于[源码](https://github.com/mxb360/eregec)树的[client/python](https://github.com/mxb360/eregec/blob/master/client/python)目录里。  


### 快速开始
将eregec.py添加到你的项目里


#### 使用方法
* 导包：`form eregec import Eregec, UserInformation, PlatformInformation`
* 创建Eregec实例：`eregec = Eregec(服务器域名 或者 IP:端口)`
* 登录：`eregec.login(用户名, 密码)`
* 从服务器更新平台数据：`eregec.updatePlatformData()`
* 取出需要的数据，如温度：`temperature = eregec.getFloatData("temperature")`
* 向硬件平台发送命令：`eregec.sendCommand(命令字符串)`
* 用户登出：`eregec.logout()`


#### 示例代码
（与Java接口简单例子非常相似，暂时略）

### 所有API

#### 类Eregec:

#### Eregec(host)
* 参数：
    * host: str类型，服务器域名或者IP:端口
* 功能：
    * 构造方法，创建一个Eregec实例，初始化用户客户端

#### login(userName, password)
* 参数：
    * userName: str类型，用户名
    * password: str类型，密码
* 功能:
    * 用户登录服务器
* 返回：
    * 登录成功返回True，失败返回False（可用getErrorMessage()获取失败原因字符串描述）

#### logout()
* 参数：
    * 无
* 功能:
    * 用户登出
* 返回：
    * 无

#### getUserId() 
* 参数：无
* 功能：
    * 获取用户ID
* 返回：
    * str类型，返回用户ID，失败返回None（可用getErrorMessage()获取失败原因字符串描述）

#### getErrorMessage() 
* 参数：无
* 功能：
    * 获取错误信息描述
* 返回：
    * str类型，错误信息描述字符串

#### getIntegerPlatformData(name) 
* 参数：
*   name: str类型数据名
* 功能：
    * 根据数据名取出相应数据
* 返回：
    * int类型，返回相应数据，失败返回None（可用getErrorMessage()获取失败原因字符串描述）

#### getFloatPlatformData(name) 
* 参数：
*   name: 数据名
* 功能：
    * 根据数据名取出相应数据
* 返回：
    * float类型，返回相应数据，失败返回None（可用getErrorMessage()获取失败原因字符串描述）

#### getStringPlatformData(name) 
* 参数：
*   name: 数据名
* 功能：
    * 根据数据名取出相应数据
* 返回：
    * str类型，返回相应数据，失败回None（可用getErrorMessage()获取失败原因字符串描述）

#### getPlatformInformation() 
* 参数：
*   无
* 功能：
    * 获取平台信息
* 返回：
    * PlatformInformation类型，返回平台信息（可用getErrorMessage()获取失败原因字符串描述）

#### getUserInformation() 
* 参数：
*   无
* 功能：
    * 获取用户信息
* 返回：
    * UserInformation类型，返回平台信息（可用getErrorMessage()获取失败原因字符串描述）

#### isLogin()
* 参数：无
* 功能：
    * 判断当前是否登录状态
* 返回：
    * 如果处于登录状态，返回True，否则返回False

#### sendCommand(command)
* 参数：
    * command: str类型命令字符串
* 功能：
    * 向平台发送指定命令
* 返回：
    * 成功返回True，失败返回False（可用getErrorMessage()获取失败原因字符串描述）

#### downloadPlatformData()
* 参数：
    * 无
* 功能：
    * 下载更新平台数据
* 返回：
    * 成功返回True，失败返回False（可用getErrorMessage()获取失败原因字符串描述）