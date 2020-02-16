# Python语言接口

为了方便硬件平台的开发，这里提供了连接服务器的Python3接口(封装服务器的socket协议)。  
提供本代码的目的是方便用户使用Python3语言快速的开发硬件平台。

### 代码

此Python3硬件平台API代码位于[源码](https://github.com/mxb360/eregec)树的[platform/python](https://github.com/mxb360/eregec/tree/master/platform/python)目录里的[eregec.py](https://github.com/mxb360/eregec/tree/master/platform/python/eregec.py)里。

### 环境搭建

要成功使用本代码，需要安装有python3（linux一般自带）
并且要安装库python3-opencv：
```shell
sudo apt install python3-opencv
```


### 快速开始
将eregec.py添加到你的项目里

#### 使用方法
* 导入eregec.py里的PlatformClient类：`form eregec import PlatformClient`
* 创建PlatformClient对象：`platform_client = PlatformClient(服务器IP, 服务器端口)`
* 设置命令回调函数：`set_command_callback(回调函数)`
* 连接服务器：`platform_client.connect(用户名, 密码)`
* 设置浮点数据：`platform_client.set_float_data(数据名称, 数据值)`
* 上传数据：`platform_cilent.upload_data()`
* 断开服务器：`platform_cilent.disconnect()`

#### 简单例子
（与C语言接口简单例子非常相似，暂时略）


### 所有API

类PlatformClient可用的方法：

#### PlatformClient(name, password, host, port)
* 参数：
    * name: str类型，用户名
    * password: str类型，用户密码
    * host: str类型，服务器IP
    * port: int类型，服务器端口
* 功能：
    * 构造方法，创建一个PlatformClient实例，初始化平台客户端
* 返回：
    * PlatformClient实例

#### connect()
* 参数：
    * 无
* 功能：
    * 连接服务器，此函数会同时连接所有socket
    * 如果服务器已经连接，会断开之前的连接，然后重新连接
* 返回：
    * 如果任意一条socket连接成功，返回True，否则返回False

#### connect_command_socket()
* 参数：
    * 无
* 功能：
    * 与服务器建立Command Socket连接
    * 如果Command Socket已经连接，会断开之前的连接，然后重新连接
* 返回：
    * 如果连接成功，返回True，否则返回False

#### connect_data_socket()
* 参数：
    * 无
* 功能：
    * 与服务器建立Data Socket连接
    * 如果Data Socket已经连接，会断开之前的连接，然后重新连接
* 返回：
    * 如果连接成功，返回True，否则返回False

#### disconnect()
* 参数：
    * 无
* 功能：
    * 与服务器断开链接，此函数会断开所有已连接的socket
* 返回：
    * None

#### disconnect_command_socket()
* 参数：
    * 无
* 功能：
    * 断开与服务器之间的Command Socket连接
* 返回：
    * None

#### disconnect_data_socket()
* 参数：
    * 无
* 功能：
    * 断开与服务器之间的Data Socket连接
* 返回：
    * None

#### is_command_socket_connected()
* 参数：
    * 无
* 功能：
    * 判断当前的Command Socket是否处于连接状态
* 返回：
    * True表示已连接，False表示未连接

#### is_connected()
* 参数：
    * 无
* 功能：
    * 判断当前的是否有socket处于连接状态
* 返回：
    * True表示有，False表示没有

#### set_command_callback(callback_func)
* 参数：
    * callback_func：
        * 参数：
            * cmd: str类型，服务器传来的命令
        * 功能：
            * 执行命令
            * 此函数执行时间不能过长，因为服务器等到此函数返回时才会应答客户端
        * 返回：
            * 如果执行成功返回"OK"，否则返回错误字符串描述。
* 功能：
    * callback_func执行时间不能过长，因为服务器等到callback_func返回时才会应答客户端
    * 如果不调用此函数，或者callback_func被设为None，命令将会被忽略，并告知服务器命令执行失败
* 返回：
    * None

#### set_int_data(name, value)
* 参数：
    * name: str类型，数据名称
    * value: int类型，数据值
* 功能：
    * 告诉平台客服端当前的数据值
    * 注意：调用此函数之后，不会立即将数据上传服务器，而是调用upload_data()时上传所有数据
* 返回：
    * None

#### set_float_data(name, value)
* 参数：
    * name: str类型，数据名称
    * value: float类型，数据值
* 功能：
    * 告诉平台客服端当前的数据值
    * 注意：调用此函数之后，不会立即将数据上传服务器，而是调用upload_data()时上传所有数据
* 返回：
    * None

#### set_string_data(name, value)
* 参数：
    * name: str类型，数据名称
    * value: str类型，数据值
* 功能：
    * 告诉平台客服端当前的数据值
    * 注意：调用此函数之后，不会立即将数据上传服务器，而是调用upload_data()时上传所有数据
* 返回：
    * None

#### upload_data()
* 参数：
    * 无
* 功能：
    * 上传设置了的数据
    * 如果设置的数据没有发生变化，此函数不会上传这个数据
    * 如果设置的所有数据都没有发生变化，此函数什么也不会做
    * 为了数据的及时性，在设置完成相关数据之后应该立即调用此函数
* 返回：
    * 如果上传成功，返回True，否则返回False（可用get_error_message()获取失败原因）