import threading
# platform.py
# 平台socket服务端和平台数据接收


import socket

from api import config

# 平台socket类型
# 平台和服务器建立两条TCP Socket作为普通数据传输
# Data Socket用于上传数据
# Cammand Socket用于下发命令
DataSocket = 0
CommandSocket = 1

# 平台服务器
class PlatformServer:
    # _platform保存所有在线的平台对象
    _platform = []

    # 平台服务器实例，应该只有一个
    _platform_server = None

    def __init__(self):
        # 等待连接的socket
        self.accept_socket = None

        # 开启一个线程，监听端口，等待平台连接
        threading.Thread(target=self._accept, daemon=True).start()

    # 运行服务器，就是创建一个PlatformServer对象
    @staticmethod
    def run_server():
        if not PlatformServer._platform_server:
            PlatformServer._platform_server = PlatformServer()
        return PlatformServer._platform_server

    # 解析socket发送的身份数据
    #
    # head:
    # 第一行：标题，是一个固定字符串："Electronic Ecological Estanciero Platform Socket"
    # 第二行：Socket类型，取值为 "Data Socket" 或者 "Cammand Socket"
    # 第三行：平台名称，如："RaspberryPi", 或者 "Windows 7", "Ubuntu 16.04" ...
    # 第四行：设备ID号
    # 第五行：结束标记，固定为"End"
    @staticmethod
    def _parse_head(head_string):
        title = 'Electronic Ecological Estanciero Platform Socket'
        socket_type = ['Data Socket', 'Cammand Socket']
        end = 'end'
        res = {}

        head = head_string.splitlines()
        if len(head) != 5 or head[0] != title or head[1] not in socket_type or head[4] != end:
            return
        res['type'] = socket_type.index(head[1])
        res['platform'] = head[2]        
        res['id'] = head[3]     

        return res   

    # 通过平台id找到在线的平台对象
    @staticmethod
    def get_platform_by_id(id):
        for platform in PlatformServer._platform:
            if platform.id == id:
                return platform

    # 将指定id的平台移除，表示平台下线
    @staticmethod
    def del_platform_by_id(id):
        for platform in PlatformServer._platform:
            if platform.id == id:
                PlatformServer._platform.remove(platform)
                return

    @staticmethod
    def close_all_platform():
        for platform in PlatformServer._platform:
            platform.close()
        PlatformServer._platform.clear()

    # 监听端口，等待平台的连接
    def _accept(self):
        print('PlatformServer Thread is start running ...')

        self.accept_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.accept_socket.bind(("0.0.0.0", config.platform_socket_port))
        self.accept_socket.listen(config.platform_socket_max_listen)

        print('PlatformServer: Socket bind in port:', config.platform_socket_port)

        while True:
            client, addr = self.accept_socket.accept()
            print('接收到Socket连接:', addr)

            try:
                head_string = client.recv(1024).decode()
                res = self._parse_head(head_string)
                if res:
                    client.send(b'OK')
                else:
                    client.send(b'error: Bad head')
                    client.close()
                    continue

                # 将socke发来的身份信息填充到平台对象
                # 并将其添加的在线平台列表里
                platform = self.get_platform_by_id(res['id'])
                if not platform:
                    platform = Platform(res['id'], res['type'])
                if res['type'] == DataSocket:
                    if platform.data_socket:
                        platform.data_socket.close()
                    platform.data_socket = client
                    print('%s: Data Socke 已建立' % platform)
                elif res['type'] == CommandSocket:
                    if platform.command_socket:
                        platform.data_socket.close()
                    platform.command_socket = client
                    print('%s: Cammand Socke 已建立'% platform)

                if platform not in self._platform:
                    self._platform.append(platform)

                if platform.data_socket and platform.command_socket:
                    print("%s: 所有socket创建完成！" % platform)
            except Exception:
                raise


# 平台上报的数据
# temperature: 温度数据
class PlatformData:
    def __init__(self):
        self.temperature = 0.0

    # 获取平台的当前的上报数据
    # temperature: 当前温度值
    def get_data(self):
        return {
            "temperature": self.temperature,
        }

# 平台对象，表示一个在线的平台
class Platform:
    def __init__(self, id, platform=''):
        self.id = id
        self.platform = platform

        self.data_socket = None
        self.command_socket = None

        self.data = PlatformData()

        # 保存要发送给平台的命令，为空表示没有命令
        # 命令发送成功之后会将cmd置空
        self.cmd = None

        # 处理上报的数据和发送指定的命令
        self.run()

    def __str__(self):
        return 'Platform(id=%s, platform=%s)' % (self.id, self.platform)

    # 获取平台的当前的上报数据
    def get_data(self):
        if not self.data_socket:
            return None, "data socket has been disconnected"
        return self.data.get_data(), ""

    # 向平台发送一个命令
    # 在这里将命令写入cmd里，run函数发现cmd不为空时会通过command_socket发送命令
    def send_cmd(self, cmd):
        if not self.command_socket:
            return "command socket socket has been disconnected"
        try:
            self.command_socket.send(cmd.encode())
            res = self.command_socket.recv(100).decode()
            if res == "":
                self.command_socket.close()
                self.command_socket = None
                return "command socket has been disconnected"
            elif res == 'OK':
                return ""
            return res
        except BrokenPipeError as e:
            print("%s: Command Socket 已断开！" % self)
            self.command_socket.close()
            self.command_socket = None
            return "%s" % e

        except Exception:
            raise

    # 断开链接
    def colse(self):
        if self.command_socket:
            self.command_socket.close()
            self.command_socket = None
        if self.data_socket:
            self.data_socket.close()
            self.data_socket = None

    # 解析data_socket接收到的平台上报的数据
    # data_socket一次性上报所有的数据
    #
    # 上报格式
    # 第一行：标题，固定字符串："Platform Data"
    # 第二行：温度值：如 "37.5"
    # 第三行：结束标记：固定字符串："End"
    def _parse_data(self, data_string):
        title = 'Platform Data'
        end = 'End'
        lines = 3

        data = data_string.splitlines()
        if len(data) != lines or data[0] != title or data[lines - 1] != end:
            return '数据格式不正确'

        try:
            self.data.temperature = float(data[1])
        except ValueError:
            return '无法解析的温度值'
        
        return "OK"
        
    # 开启一个线程用于接收平台上报的数据以及向平台发送命令
    def run(self):
        def _run():
            print('Data Socket Platform Thread is start running ...')

            while self.data_socket:
                # 接收上报的数据s
                # 如果接收成功，服务器应答OK
                # 否则服务器应答错误信息
                try:
                    data = self.data_socket.recv(1024).decode()
                    res = self._parse_data(data)
                    self.data_socket.send(res.encode())
                except BrokenPipeError as e:
                    print("%s: Data Socket 已断开:" % self, e)
                    self.data_socket.close()
                    self.data_socket = None
                except Exception:
                    raise

            # 两条socket均断开，认为平台已下线
            #print("%s: 客户端已下线" % self)
            #PlatformServer.del_platform_by_id(self.id)
            #break

            #print('%s Thread was stoped' % self)

        # 开线槽执行上述过程
        threading.Thread(target=_run, daemon=True).start()
