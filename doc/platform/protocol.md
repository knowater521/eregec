# 硬件通信协议

### 概述

硬件平台与服务器通过TCP socket连接。  
服务器对socket连接的默认监听端口：51435。   
监听端口由[源码](https://github.com/mxb360/eregec)文件[server/eregec/api/config.py](https://github.com/mxb360/eregec/blob/master/server/eregec/api/config.py)里的platform_socket_port变量值决定。  
  
硬件平台和服务器通过不同的socket连接完成不同的数据传输功能：  
* Data Socket：一条单独的socket用于硬件平台向服务器发送实时数据（不包括视频图像）。  
* Command Socket：一条单独的socket用于服务器向硬件平台发送命令。  
  
这些socket可以不用全部连接，此时没有连接的socket的相关功能将无法为客户端提供。  
服务器从启动开始，便会一直监听指定的端口，等待硬件平台的连接。  
硬件平台可以随时建立某条socket，可以随时断开某条socket。  
  
### socket连接协议

硬件平台主动向服务器发起连接请求；  
连接成功后，服务器会应答字符串："Electronic Ecological Estanciero Server"；  
硬件平台一次性发送由字符串组成的完整的请求头；  
服务器根据请求头识别是哪种socket；  
如果请求头不合法，服务器应答错误信息字符串并关闭连接；  
如果请求头被正确解析，服务器应答字符串："OK"，并保持连接。   
  
请求头组成： 
* 第一行：标题，是一个固定字符串："Electronic Ecological Estanciero Platform Socket"  
* 第二行：Socket类型，取值为 "Data Socket"，"Cammand Socket"  
* 第三行：平台名称，如："RaspberryPi", 或者 "Windows 7", "Ubuntu 16.04"等  
* 第四行：设备ID号（ID号用于关联硬件平台和用户，在用户配置里设置）  
* 第五行：结束标记，固定为"End"  
  
一个完整的请求头的例子：
```
Electronic Ecological Estanciero Platform Socket
Data Socket
RaspberryPi
eregecuserplatform
End
```

### socket通信协议

#### Data Socket：  
* 硬件平台通过此socket将数据发送给服务器  
* 硬件平台不需要一直向服务器发送平台数据  
* 不过为了信息的及时性，硬件平台应该及时发送发生变动的平台数据   
  
#### Data Socket 通信协议：   
* 硬件平台发送以下格式的字符串数据包：  
* 第一行：标题，固定字符串："Platform Data"；  
* 中间任意行：一条平台数据，格式："数据名称:数据值"。即数据名称和值之间通过英文字符':'连接；  
* 最后一行：结束标记：固定字符串："End"；  
* 服务器解析数据包，如果数据包格式不正确，服务器应答错误信息，否则服务器应答"OK"。

一个完整的数据包的例子：
```
Platform Data
temperature:37.5
End
```
  
#### Command Socket：  
* 服务器通过此socket将数据发送给硬件平台。  
* 当服务器收到用户客户端发送的命令字符串后，会通过此socket将命令发送给硬件平台。  
* 如果服务器收到用户客户端发送的命令字符串时此socket未连接，服务器返回给客户端命令执行失败的消息。  

#### Command Socket 通信协议：  
* 服务器将命令字符串一次性发给硬件平台；  
* 如果硬件平台认为此命令没有问题，应答"OK"，否则向服务器应答错误字符串。  
