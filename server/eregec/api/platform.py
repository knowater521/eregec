# platform.py
# 平台socket服务端和平台数据接收

import threading
import socket
import numpy as np;
import cv2

from api import config, api
from api.user import User

# 平台socket类型
# 平台和服务器建立两条TCP Socket作为普通数据传输
# Data Socket用于上传数据
# Cammand Socket用于下发命令
DataSocket = 0
CommandSocket = 1
ImageSocket = 2
SOCKET_NAME = ['Data Socket', 'Command Socket', 'Image Socket']

# 平台服务器
class PlatformServer:
    # _platform保存所有在线的平台对象
    _platform = []

    # 平台服务器实例，应该只有一个
    _platform_server = None

    def __init__(self):
        # 等待连接的socket
        self.accept_socket = None

        try:
            api.pinfo("PlatformServer Config:")
            for _config in dir(config):
                if not _config.startswith('_'):
                    api.pinfo("    {} = {}".format(_config, getattr(config, _config)))
            print()
            
            self.accept_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.accept_socket.bind(('0.0.0.0', config.platform_socket_port))
            self.accept_socket.listen(config.platform_socket_max_listen)
        except Exception as e:
            import os
            api.perror('平台服务器PlatformServer启动失败：{}'.format(e))
            os._exit(1)

        # 开启一个线程，监听端口，等待平台连接
        threading.Thread(target=self.__accept, daemon=True).start()

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
    # 第三行：用户名
    # 第四行：用户密码
    # 第五行：结束标记，固定为"End"
    @staticmethod
    def _parse_head(head_string):
        title = 'Electronic Ecological Estanciero Platform Socket'
        end = 'End'
        res = {}

        head = head_string.splitlines()
        if len(head) != 5 or head[0] != title or (head[1] not in SOCKET_NAME) or head[4] != end:
            return
        res['type'] = SOCKET_NAME.index(head[1])
        res['name'] = head[2]
        res['password'] = head[3]

        return res   

    # 通过平台id找到在线的平台对象
    @staticmethod
    def get_platform_by_name(name):
        for platform in PlatformServer._platform:
            if platform.name == name:
                return platform

    # 将指定id的平台移除，表示平台下线
    @staticmethod
    def del_platform_by_name(name):
        for platform in PlatformServer._platform:
            if platform.name == name:
                PlatformServer._platform.remove(platform)
                return

    @staticmethod
    def close_all_platform():
        for platform in PlatformServer._platform:
            platform.close()
        PlatformServer._platform.clear()

    # 监听端口，等待平台的连接
    def __accept(self):
        api.pinfo('PlatformServer Thread is start running ...')
        api.pinfo('PlatformServer: Socket bind in port: {}'.format(config.platform_socket_port))

        while True:
            client, addr = self.accept_socket.accept()
            api.pinfo('accept(): Get Socket connect: {}'.format(addr))
            threading.Thread(target=self.__check_head, args=(client, addr), daemon=True).start()

    def __check_head(self, client, addr):
        try:
            client.send(b'Electronic Ecological Estanciero Server')
            head_string = client.recv(1024).decode()
            res = self._parse_head(head_string)
            if not res:
                client.send(b'Bad head')
                client.close()
                #api.perror('{} Connection refused! Bad head: "{}"'.format(addr, head_string.replace('\n', '\\n')))
                return
            # 将socke发来的身份信息填充到平台对象
            # 并将其添加的在线平台列表里
            #api.pinfo('{} head: "{}"'.format(addr, head_string.replace('\n', ' || ')))
            user, err = User.get_user(res['name'], res['password'], False)
            if err:
                client.send(err.encode())
                return
            client.send(b'OK')

            platform = PlatformServer.get_platform_by_name(res['name'])
            if not platform:
                api.pinfo('create new platform object for name "{}"'.format(res['name']))
                platform = Platform(res['name'], user)

            if res['type'] == DataSocket:
                if platform.data_socket:
                    api.pwarning("old Data Socket found, close it")
                    platform.data_socket.close()
                platform.data_socket = client
                api.pinfo('{}: Data Socke Connected'.format(platform))
                platform.watch_data_socket()
            elif res['type'] == CommandSocket:
                if platform.command_socket:
                    api.pwarning("old Command Socket found, close it")
                    platform.command_socket.close()
                platform.command_socket = client
                api.pinfo('{}: Cammand Socke Connected'.format(platform))
            elif res['type'] == ImageSocket:
                if platform.image_socket:
                    api.pwarning("old Image Socket found, close it")
                    platform.image_socket.close()
                platform.image_socket = client
                api.pinfo('{}: Image Socke Connected'.format(platform))
                platform.watch_image_socket()

            if platform not in self._platform:
                api.pinfo('add new platform object into PlatformServer')
                self._platform.append(platform)
        except Exception:
            raise


# 平台对象，表示一个在线的平台
class Platform:
    def __init__(self, name, user=None):
        self.data_active = False
        self.image_active = False
        self.name = name
        self.user = user
        self.data_socket = None
        self.command_socket = None
        self.image_socket = None

        self.data = {}
        self.img_data = b''

    def __str__(self):
        return 'Platform{{name="{}"}}'.format(self.name)

    # 获取平台的当前的上报数据
    def get_data(self):
        if not self.data_socket:
            return None, 'data socket has been disconnected'
        return self.data, ''

    # 获取平台信息
    def get_info(self):
        return self.user.platform_info if self.user else {}

    # 向平台发送一个命令
    # 在这里将命令写入cmd里，run函数发现cmd不为空时会通过command_socket发送命令
    def send_cmd(self, cmd):
        if not self.command_socket:
            return 'command socket socket has been disconnected'
        try:
            self.command_socket.send(cmd.encode())
            res = self.command_socket.recv(100).decode()
            if res == '':
                self.command_socket.close()
                self.command_socket = None
                api.pwarning("{}: Command Socket 已断开！".format(self))
                return 'command socket has been disconnected'
            elif res == 'OK':
                return ''
            return res
        except (BrokenPipeError, ConnectionResetError) as e:
            api.pwarning("{}: Command Socket 已断开！".format(self))
            self.command_socket.close()
            self.command_socket = None
            return "{}".format(e)

        except Exception:
            api.perror("%s: Command Socket 已断开！" % self)
            self.command_socket.close()
            self.command_socket = None
            raise

    # 断开链接
    def colse(self):
        if self.command_socket:
            self.command_socket.close()
            self.command_socket = None
        if self.data_socket:
            self.data_socket.close()
            self.data_socket = None
        if self.image_socket:
            self.image_socket.close()
            self.image_socket = None

    # 解析data_socket接收到的平台上报的数据
    # data_socket一次性上报所有的数据
    #
    # 上报格式
    # 第一行：标题，固定字符串："Platform Data"
    # 中间任意行：一条平台数据，格式："数据名称:数据类型:数据值"。分割符为英文字符':'； 
    # 数据类型包含：int、float、string三类；
    # 最后一行：结束标记：固定字符串："End"
    def _parse_data(self, data_string):
        title = 'Platform Data'
        end = 'End'

        data = data_string.splitlines()
        if not data or data[0].strip() != title or data[-1].strip() != end:
            return 'Data Format Error: Bad start string or end string'

        try:
            for data_string in data[1:-1]:
                data_string = data_string.strip()
                if not data_string:
                    continue
                data_tokens = data_string.split(':')
                if len(data_tokens) != 3:
                    return 'Data Format Error: %s: Should be NAME:TYPE:VALUE' % data_string
                data_name = data_tokens[0].strip()
                data_type = data_tokens[1].strip()
                data_value = data_tokens[2].strip()
                if data_type == 'int':
                    data_value = int(data_value)
                elif data_type == 'float':
                    data_value = float(data_value)
                elif data_type != 'string':
                    return 'Data Format Error: {}: Unknown type'.format(data_string)
                self.data[data_name] = data_value
        except ValueError as e:
            return 'Data Format Error: {}: {}'.format(data_string, e)
        return 'OK'
        
    # 开启一个线程用于接收平台上报的数据以及向平台发送命令
    def watch_data_socket(self):
        def _run_data_socket():
            api.pinfo('{} Data Socket Thread is start running ...'.format(self))

            if self.data_active:
                return

            self.data_active = True
            while self.data_socket and self.data_active:
                # 接收上报的数据s
                # 如果接收成功，服务器应答OK
                # 否则服务器应答错误信息
                try:
                    data = self.data_socket.recv(1024).decode()
                    if data:
                        res = self._parse_data(data)
                        if res != 'OK':
                            api.pwarning('data package parse failed: {}'.format(res))
                            api.pwarning('data package: "{}"'.format(data))
                        self.data_socket.send(res.encode())
                except (BrokenPipeError, ConnectionResetError) as e:
                    api.pwarning('{}: Data Socket 已断开: {}'.format(self, e))
                    self.data_socket.close()
                    self.data_socket = None
                except Exception as e:
                    api.perror('{}: Data Socket 已断开: {}'.format(self, e))
                    self.data_socket.close()
                    self.data_socket = None
                    raise

            self.data_active = False
            api.pinfo('{} Data Socket Thread stoped'.format(self))
        
        threading.Thread(target=_run_data_socket, daemon=True).start()
        
    def watch_image_socket(self):
        def _run_image_socket():
            api.pinfo('{} Image Socket Thread is start running ...'.format(self))

            if self.image_active:
                return

            self.image_active = True
            while self.image_socket and self.image_active:
                try:
                    data = self.image_socket.recv(16)
                    if data:
                        try:
                            img_len = int(data.decode())
                            _len = img_len
                        except:
                            #api.perror("image size unknown")
                            continue

                        img_data = b''
                        buf = b''
                        while img_len:
                            buf = self.image_socket.recv(img_len)
                            if buf:
                                img_len -= len(buf)
                                img_data += buf
                        img = img_data#np.fromstring(img_data, np.uint8)
                        #img = cv2.imdecode(img, 1)
                        
                        self.img_data = img#.tobytes()
                        
                        api.pinfo("get image: {}({})".format(len(img), _len))
                except (BrokenPipeError, ConnectionResetError) as e:
                    api.pwarning('{}: Image Socket 已断开: {}'.format(self, e))
                    self.image_socket.close()
                    self.image_socket = None
                except OSError as e:
                    api.perror('{}: OSError: {}'.format(self, e))
                    pass
                except Exception as e:
                    api.perror('{}: Image Socket 已断开: {}'.format(self, e))
                    self.image_socket.close()
                    self.image_socket = None
                    raise

            self.image_active = False
            api.pinfo('{} Data Socket Thread stoped'.format(self))

        threading.Thread(target=_run_image_socket, daemon=True).start()

    def get_image_data(self):
        return self.img_data