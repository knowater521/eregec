# C语言接口

为了方便硬件平台的开发，这里提供了连接服务器的C语言接口(封装服务器的socket协议)。  
提供本代码的目的是方便用户使用C语言或者C++语言快速的开发硬件平台。


### 代码

此C语言硬件平台API代码位于[源码](https://github.com/mxb360/eregec)树的[platform/c](https://github.com/mxb360/eregec/tree/master/platform/c)目录里。  


要成功使用本代码，需要安装以下库：


### 快速开始
将eregec.c eregec.h添加到你的项目里  
   
在linux下编译链接代码时，需要链接库: -lpthread  
在Windows下使用gcc编译链接代码时，需要链接库: -lWs2_32

#### 使用方法
* 包含头文件：`#include "eregec.h"`
* 初始化客户端：`eregec_init(用户名, 密码, 服务器IP, 服务器端口)`
* 设置命令回调函数：`eregec_set_command_callback(回调函数)`
* 连接服务器：`eregec_connect()`
* 设置浮点数据：`eregec_set_float_data(数据名称, 数据值)`
* 上传数据：`eregec_upload_data()`
* 断开服务器：`eregec_disconnect()`

#### 简单例子
这里提供Linux版本的示例。  
（对于Windows，把unistd.h换成Windows.h，sleep(1)改成Sleep(1000)即可）

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* 你需要包含此头文件来使用提供的API接口 */
#include "eregec.h"

/* 自定义的命令回调函数(通过eregec_set_command_callback设置)
 * 当收到用户发送的命令后，此函数会被执行，参数即为当前命令
 * 这里演示的是用户发送"open-led"便开灯，"close-led"关灯，其他为无效命令
 * 这里对开关灯的演示就是打印出“开灯！”, “关灯！”
 * 如果命令执行成功，请返回COMMAND_OK(描述信息)，失败请返回COMMAND_FAILED(描述信息)
 */
const char *resolve_command(const char *cmd)
{
    if (!strcmp(cmd, "open-led")) {
        printf("开灯！\n");
    } else if (!strcmp(cmd, "close-led")) {
        printf("关灯！\n");
    } else {
        printf("%s: 不能识别的命令\n", cmd);
        return COMMAND_FAILED("unkown command!");
    }
    return COMMAND_OK("succeed!");
}

int main(void)
{
    /* 平台客户端的初始化，在使用提供的函数之前，必须初始化平台客户端
     * eregec_init(用户名, 密码, 服务器IP, 服务器端口)
     */
    eregec_init("eregec", "123456", "39.108.3.243", 51435);

    /* 连接服务器
     * 使用此函数时，终端会输出连接信息
     * 如果连接成功，返回true，否则返回false，终端会输出连接信息
     */
    if (!eregec_connect()) {
        printf("Error: Connect Server Failed!\n");
        return 1;
    }

    /* 指定命令回调函数是resolve_command
     * 如果不调用此函数设置命令回调函数，命令将会被忽略。
     */
    eregec_set_command_callback(resolve_command);

    /*eregec_is_connected()判断是否处于连接中  */
    while (eregec_is_connected()) {
        /* 设置平台数据，这里采用随机数模拟真实值
         * float类型的数据采用函数eregec_set_float_data设置
         * eregec_set_float_data(数据名称, 数据值)
         */ 
        eregec_set_float_data("temperature", 37 + (rand() % 10) / 10.0);
        eregec_set_float_data("humidity", 18 + (rand() % 100)/ 100.0);
        
        /* 将设置的数据上传服务器 */
        eregec_upload_data();

        /* 延时一秒，这里每隔一秒更新一次数据 */
        sleep(1);
    }

    /* 断开与服务器的所有连接 */
    eregec_disconnect();
	return 0;
}
```

### 所有API

#### void eregec_init(const char \*name, const char \*password, const char \*host, int port)
* 参数：
    * name: 用户名
    * password: 用户密码
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
    * 如果任意一条socket连接成功，返回true，否则返回false

#### bool eregec_connect_command_socket(void)
* 参数：
    * 无
* 功能：
    * 与服务器建立Command Socket连接
    * 如果Command Socket已经连接，会断开之前的连接，然后重新连接
* 返回：
    * 如果连接成功，返回true，否则返回false

#### bool eregec_connect_data_socket(void)
* 参数：
    * 无
* 功能：
    * 与服务器建立Data Socket连接
    * 如果Data Socket已经连接，会断开之前的连接，然后重新连接
* 返回：
    * 如果连接成功，返回true，否则返回false

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

#### bool eregec_is_command_socket_connected(void)
* 参数：
    * 无
* 功能：
    * 判断当前的Command Socket是否处于连接状态
* 返回：
    * true表示已连接，false表示未连接

#### bool eregec_is_data_socket_connected(void)
* 参数：
    * 无
* 功能：
    * 判断当前的Data Socket是否处于连接状态
* 返回：
    * true表示已连接，false表示未连接

#### bool eregec_is_connected(void)
* 参数：
    * 无
* 功能：
    * 判断当前的是否有socket处于连接状态
* 返回：
    * true表示有，false表示没有

#### void eregec_set_command_callback(const char \*(\*callback_func)(const char \*cmd))
* 参数：
    * callback_func：
        * 参数：
            * cmd: 服务器传来的命令
        * 功能：
            * 执行命令
            * 此函数执行时间不能过长，因为服务器等到此函数返回时才会应答客户端
        * 返回：
            * 如果执行成功返回COMMAND_OK(字符串描述)，否则返回COMMAND_FAILED(错误字符串描述)。
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
