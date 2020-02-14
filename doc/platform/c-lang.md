# C语言接口

为了方便硬件平台的开发，这里提供了连接服务器的C语言接口(封装服务器的socket协议)。  
提供本代码的目的是方便用户使用C语言或者C++语言快速的开发硬件平台。


### 代码

此C语言硬件平台API代码位于[源码](https://github.com/mxb360/eregec)树的[eregec/c/api](https://github.com/mxb360/eregec/blob/master/eregec/c/api)目录里。  


要成功使用本代码，需要安装opencv库：


### 快速开始
将eregec.c eregec.h添加到你的项目里  
   
在链接代码时，需要链接库: 

#### 使用方法
* 包含头文件：`#include "eregec.h"`
* 初始化客户端：`eregec_init(平台ID, 平台名, 服务器IP, 服务器端口)`
* 设置命令回调函数：`eregec_set_command_callback(回调函数)`
* 连接服务器：`eregec_connect()`
* 设置当前温度：`eregec_set_temperature(当前温度)`
* 上传数据：`eregec_upload_data()`
* 断开服务器：`eregec_disconnect()`


### 所有API

#### void eregec_init(const char \*id, const char \*name, const char \*host, int port)
* 参数：
    * id: 平台ID
    * name: 平台名字，如"RaspberryPi"，可任意设定
    * host: 服务器IP
    * port: 服务器端口
* 功能：
    * 初始化平台客户端
* 返回：
    * 无

#### bool eregec_connect(void)
* 参数：
    * 无
* 功能：
    * 连接服务器，此函数会同时连接所有socket
    * 如果服务器已经连接，会断开之前的连接，然后重新连接
* 返回：
    * 如果任意一条socket连接成功，返回true，否则返回false（可用eregec_get_error_message()获取失败原因）

#### bool eregec_connect_command_socket(void)
* 参数：
    * 无
* 功能：
    * 与服务器建立Command Socket连接
    * 如果Command Socket已经连接，会断开之前的连接，然后重新连接
* 返回：
    * 如果连接成功，返回true，否则返回false（可用eregec_get_error_message()获取失败原因）

#### bool eregec_connect_data_socket(void)
* 参数：
    * 无
* 功能：
    * 与服务器建立Data Socket连接
    * 如果Data Socket已经连接，会断开之前的连接，然后重新连接
* 返回：
    * 如果连接成功，返回true，否则返回false（可用eregec_get_error_message()获取失败原因）

#### void eregec_disconnect(void)
* 参数：
    * 无
* 功能：
    * 与服务器断开链接，此函数会断开所有已连接的socket
* 返回：
    * 无

#### void eregec_disconnect_command_socket(void)
* 参数：
    * 无
* 功能：
    * 断开与服务器之间的Command Socket连接
* 返回：
    * 无

#### void eregec_disconnect_data_socket(void)
* 参数：
    * 无
* 功能：
    * 断开与服务器之间的Data Socket连接
* 返回：
    * 无

#### const char \*eregec_get_error_message(void)
* 参数：
    * 无
* 功能：
    * 获取出错信息
    * eregec_connet系列函数返回false时，可通过此函数获取错误信息
    * eregec_upload_data函数返回false时，可通过此函数获取错误信息
* 返回：
    * 返回错误信息字符串

#### bool eregec_is_command_socket_connected(void)
* 参数：
    * 无
* 功能：
    * 判断当前的Command SOcket是否处于连接状态
* 返回：
    * true表示已连接，false表示未连接

#### bool eregec_is_socket_connected(void)
* 参数：
    * 无
* 功能：
    * 判断当前的是否有socket处于连接状态
* 返回：
    * true表示有，false表示没有

#### void eregec_set_cmd_callback(const char \*(\*callback_func)(const char \*cmd))
* 参数：
    * callback_func：
        * 参数：
            * cmd: 服务器传来的命令
        * 功能：
            * 执行命令
            * 此函数执行时间不能过长，因为服务器等到此函数返回时才会应答客户端
        * 返回：
            * 如果执行成功返回"OK"，否则返回错误字符串描述。
* 功能：
    * callback_func执行时间不能过长，因为服务器等到callback_func返回时才会应答客户端
    * 如果不调用此函数，或者callback_func被设为NULL，命令将会被忽略，并告知服务器命令执行失败
* 返回：
    * 无

#### void eregec_set_int_data(const char \*name, int value)
* 参数：
    * name: 数据名称，最好为一个英文单词
    * value: 数据值
* 功能：
    * 告诉平台客服端当前的数据值
    * 注意：调用此函数之后，不会立即将数据上传服务器，而是调用eregec_upload_data()时上传所有数据
* 返回：
    * 无

#### void eregec_set_float_data(const char \*name, float value)
* 参数：
    * name: 数据名称，最好为一个英文单词
    * value: 数据值
* 功能：
    * 告诉平台客服端当前的数据值
    * 注意：调用此函数之后，不会立即将数据上传服务器，而是调用eregec_upload_data()时上传所有数据
* 返回：
    * 无

#### void eregec_set_string_data(const char \*name, const char  \*value)
* 参数：
    * name: 数据名称，最好为一个英文单词
    * value: 数据值
* 功能：
    * 告诉平台客服端当前的数据值
    * 注意：调用此函数之后，不会立即将数据上传服务器，而是调用eregec_upload_data()时上传所有数据
* 返回：
    * 无

#### bool eregec_upload_data(void)
* 参数：
    * 无
* 功能：
    * 上传设置了的数据
    * 如果设置的数据没有发生变化，此函数不会上传这个数据
    * 如果设置的所有数据都没有发生变化，此函数什么也不会做
    * 为了数据的及时性，在设置完成相关数据之后应该立即调用此函数
* 返回：
    * 如果上传成功，返回true，否则返回false（可用eregec_get_error_message()获取失败原因）
