import socket, time
import threading
import random

# 平台socket类型
# 平台和服务器建立两条TCP Socket作为普通数据传输
# Data Socket用于上传数据
# Command Socket用于下发命令
DataSocket = 0
CommandSocket = 1

class PlatformClient:
    def __init__(self, id, name, host, port):
        self.__data_socket = None
        self.__command_socket = None
        self.__id = id
        self.__name = name
        self.__host = host
        self.__port = port
        self.__data = {}
        self.__data_buf = {}
        self.__exec_cmd_func = None
        self.__error_message = ""

    def __perror(self, err):
        print('PlatformClient: Error: ' + err)

    def __pinfo(self, err):
        print('PlatformClient: Info: ' + err)

    def __pwarning(self, err):
        print('PlatformClient: Warning: ' + err)

    # head:
    # 第一行：标题，是一个固定字符串："Electronic Ecological Estanciero Platform Socket"
    # 第二行：Socket类型，取值为 "Data Socket" 或者 "Cammand Socket"
    # 第三行：平台名称
    # 第四行：设备ID号
    # 第五行：结束标记，固定为"End"
    def __create_head(self, type):
        title = 'Electronic Ecological Estanciero Platform Socket'
        socket_type = ['Data Socket', 'Cammand Socket']
        end = 'end'

        return title + '\n' + socket_type[type] + '\n' + self.__name + '\n' + self.__id + '\n' + end

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
    
    def __connec_socket(self, server_socket, type, type_name):
        try:
            self.__pinfo("%s: Try to connect server: %s:%d" % (type_name, self.__host, self.__port))
            server_socket.connect((self.__host, self.__port))
            server_socket.send(self.__create_head(type).encode())
            res = server_socket.recv(20).decode()
            if res != 'OK':
                server_socket.close()
                self.__perror(type_name + ' connect failed: Server return: "%s"' % (type_name, res))
            return True
        except Exception as e:
            self.__perror(type_name + ' connect failed: ' + str(e))

    def connect(self):
        data_socket_ok = self.connect_data_socket()
        command_socke_ok = self.connect_command_socket()
        return data_socket_ok or command_socke_ok

    def connect_data_socket(self):
        if self.__data_socket:
            self.__data_socket.close()
        self.__data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return self.__connec_socket(self.__data_socket, DataSocket, "Data Socket")

    def connect_command_socket(self):
        if self.__command_socket:
            self.__command_socket.close()
        self.__command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.__connec_socket(self.__command_socket, CommandSocket, 'Command Socket'):
            threading.Thread(target=self._get_cmd, daemon=True).start()
            return True
        return False

    def is_connected(self):
        return self.is_data_socket_connected() or self.is_data_socket_connected()

    def is_data_socket_connected(self):
        return self.__data_socket is not None

    def is_command_socket_connected(self):
        return self.__command_socket is not None

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

    def set_int_data(self, name, value): 
        self.__data[name] = value

    def set_string_data(self, name, value): 
        self.__data[name] = value

    def set_float_data(self, name, value): 
        self.__data[name] = value

    def get_error_message(self):
        return self.__error_message

    def set_command_callback(self, callback_func):
        self.__exec_cmd_func = callback_func

    def upload_data(self):
        if self.__data_socket == None:
            self.__perror("Data Socket not connect")
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
        while self.__command_socket:
            try:
                cmd = self.__command_socket.recv(100).decode()

                self.__pinfo('get command "%s"' % cmd)
                if self.__exec_cmd_func:
                    self.__command_socket.send(self.__exec_cmd_func(cmd).encode())
                else:
                    self.__pwarning('%s: Command Ignored' % cmd)
                    self.__command_socket.send(b'command ignored')
            except BrokenPipeError:
                self.__perror("Cammand Socket Broken!")
                self.__command_socket = None
