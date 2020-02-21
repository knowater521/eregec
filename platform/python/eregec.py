import cv2
import socket, time
import threading
import random

# 平台socket类型
# 平台和服务器建立两条TCP Socket作为普通数据传输
# Data Socket用于上传数据
# Command Socket用于下发命令
DataSocket = 0
CommandSocket = 1
ImageSocket = 2
SOCKET_NAME = ['Data Socket', 'Command Socket', "Image Socket"]

class PlatformClient:
    __M_COLOR = "\033[0m"
    __E_COLOR = "\033[31m"
    __W_COLOR = "\033[35m"
    __I_COLOR = "\033[33m"
    __R_COLOR = "\033[0m"

    def __init__(self, name, password, host, port):
        self.__data_socket = None
        self.__command_socket = None
        self.__image_socket = None
        self.__password = password
        self.__name = name
        self.__host = host
        self.__port = port
        self.__data = {}
        self.__data_buf = {}
        self.__exec_cmd_func = None
        self.__is_image_start = False
        self.__image_cap = None

    def __perror(self, string):
        print(self.__M_COLOR + 'PlatformClient: ' + self.__E_COLOR + 'Error: ' + string + self.__R_COLOR)

    def __pwarning(self, string):
        print(self.__M_COLOR + 'PlatformClient: ' + self.__W_COLOR + 'Warning: ' + string + self.__R_COLOR)

    def __pinfo(self, string):
        print(self.__M_COLOR + 'PlatformClient: ' + self.__I_COLOR + 'Info: ' + string + self.__R_COLOR)

    # head:
    # 第一行：标题，是一个固定字符串："Electronic Ecological Estanciero Platform Socket"
    # 第二行：Socket类型，取值为 "Data Socket" 或者 "Cammand Socket"
    # 第三行：用户名
    # 第四行：用户密码
    # 第五行：结束标记，固定为"End"
    def __create_head(self, type):
        title = 'Electronic Ecological Estanciero Platform Socket'
        socket_type = ['Data Socket', 'Command Socket', 'Image Socket']
        end = 'End'

        return title + '\n' + socket_type[type] + '\n' + self.__name + '\n' + self.__password + '\n' + end

    # 第一行：标题，固定字符串："Platform Data"
    # 中间任意行：一条平台数据，格式："数据名称:数据类型:数据值"。分割符为英文字符':'； 
    # 数据类型包含：int、float、string三类；
    # 第三行：结束标记：固定字符串："End"
    def __create_data(self, all=False):
        title = "Platform Data"
        end = "End"

        data_string = ""
        for key, value in self.__data.items():
            if all or self.__data_buf.get(key, None) != value:
                if type(value) == type(int()):
                    data_string += key + ":int:" + str(value) + "\n"
                elif type(value) == type(float()):
                    data_string += key + ":float:" + str(value) + "\n"
                elif type(value) == type(str()):
                    data_string += key + ":string:" + value + "\n"
                self.__data_buf[key] = value
        if data_string == "":
            data_string = '\n'

        return title + '\n' + data_string + end
    
    def __connec_socket(self, server_socket, type):
        try:
            self.__pinfo("%s: Try to connect server: %s:%d" % (SOCKET_NAME[type], self.__host, self.__port))
            server_socket.connect((self.__host, self.__port))            
            if server_socket.recv(1024) != b'Electronic Ecological Estanciero Server':
                self.__perror('%s connect failed: Bad Server Return' % SOCKET_NAME[type])
            server_socket.send(self.__create_head(type).encode())
            res = server_socket.recv(20).decode()
            if res != 'OK':
                server_socket.close()
                self.__perror(SOCKET_NAME[type] + ' connect failed: Server return: "%s"' % res)
                return False
            self.__pinfo('%s is connected' % SOCKET_NAME[type])
            
            return True
        except Exception as e:
            self.__perror(SOCKET_NAME[type] + ' connect failed: ' + str(e))

    def connect(self):
        data_socket_ok = self.connect_data_socket()
        command_socke_ok = self.connect_command_socket()
        image_socket_ok = self.connect_image_socket()
        return data_socket_ok or command_socke_ok or image_socket_ok

    def connect_data_socket(self):
        if self.__data_socket:
            self.__data_socket.close()
        self.__data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not self.__connec_socket(self.__data_socket, DataSocket):
            self.__data_socket = None
            return False
        return True

    def connect_command_socket(self):
        if self.__command_socket:
            self.__command_socket.close()
        self.__command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.__connec_socket(self.__command_socket, CommandSocket):
            threading.Thread(target=self._get_cmd, daemon=True).start()
            return True
        self.__command_socket = None
        return False

    def connect_image_socket(self):
        if self.__image_socket:
            self.__image_socket.close()
        self.__image_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.__connec_socket(self.__image_socket, ImageSocket):
            threading.Thread(target=self._send_image, daemon=True).start()
            return True
        self.__image_socket = None
        return False

    def is_connected(self):
        return self.is_data_socket_connected() or self.is_data_socket_connected() or self.is_image_socket_connected()

    def is_data_socket_connected(self):
        return self.__data_socket is not None

    def is_command_socket_connected(self):
        return self.__command_socket is not None

    def is_image_socket_connected(self):
        return self.__image_socket is not None

    def disconnect(self):
        self.disconnect_data_socket()
        self.disconnect_command_socket()
        
    def disconnect_data_socket(self):
        if self.__data_socket:
            self.__data_socket.close()
            self.__data_socket = None

    def disconnect_command_socket(self):
        if self.__command_socket:
            self.__command_socket.close()
            self.__command_socket = None

    def disconnect_image_socket(self):
        if self.__image_socket:
            self.__image_socket.close()
            self.__image_socket = None

    def set_int_data(self, name, value): 
        self.__data[name] = value

    def set_string_data(self, name, value): 
        self.__data[name] = value

    def set_float_data(self, name, value): 
        self.__data[name] = value

    def set_command_callback(self, callback_func):
        self.__exec_cmd_func = callback_func

    def start_send_image(self):
        self.__is_image_start = True

    def upload_data(self):
        if self.__data_socket == None:
            self.__perror("upload_data(): Data Socket not connect")
            return

        try: 
            data = self.__create_data().encode()
            self.__data_socket.send(data)
            res = self.__data_socket.recv(100).decode()
            if res != 'OK':
                self.__perror("Upload data failed: server return: '%s'" % res)
        except BrokenPipeError:
            self.__perror("Data Socket broken!")
            self.__data_socket = None

    def _get_cmd(self):
        self.__pinfo('start Command Socket send image thread ...')
        while self.__command_socket:
            try:
                cmd = self.__command_socket.recv(100).decode()
                if not cmd:
                    raise BrokenPipeError

                self.__pinfo('get command "%s"' % cmd)
                if self.__exec_cmd_func:
                    self.__command_socket.send(self.__exec_cmd_func(cmd).encode())
                else:
                    self.__pwarning('%s: Command Ignored' % cmd)
                    self.__command_socket.send(b'command ignored')
            except BrokenPipeError:
                self.__perror('Cammand Socket Broken!')
                self.__command_socket = None
        self.__pinfo('stop Command Socket send image thread ...')

    def _send_image(self):
        self.__pinfo('start Image Socket send image thread ...')

        cnt = 0
        while self.__image_socket:
            try:
                if self.__is_image_start:
                    if not self.__image_cap:
                        self.__image_cap = cv2.VideoCapture(0)
                        self.__image_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 100)
                        self.__image_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 100)
                        self.__pinfo('Image Socket: start send image ...')

                    _, frame = self.__image_cap.read()

                    cnt = (cnt + 1) % 2
                    if cnt:
                        continue

                    _, img_encode = cv2.imencode('.jpg', frame)
                    img = img_encode.tostring()

                    self.__image_socket.send(str(len(img)).ljust(16).encode())
                    self.__image_socket.send(img)
                    self.__pinfo("send image: {}".format(len(img)))
                else:
                    if self.__image_cap:
                        self.__image_cap.release()
                        self.__image_cap = None
                        self.__pinfo('Image Socket: stop send image ...')
            except BrokenPipeError:
                self.__perror('Image Socket Broken!')
                self.__image_socket = None
        self.__pinfo('stop Image Socket send image thread ...')
