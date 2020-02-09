import socket, time
import threading
import random

# 平台socket类型
# 平台和服务器建立两条TCP Socket作为普通数据传输
# Data Socket用于上传数据
# Command Socket用于下发命令
DataSocket = 0
CommandSocket = 1

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

    def __eq__(self, other):
        return self.temperature == other.temperature

    def clone(self):
        data = PlatformData()
        data.temperature = self.temperature
        return data


class PlatformClient:
    def __init__(self, id, name, host, port):
        self._data_socket = None
        self._command_socket = None
        self._id = id
        self._name = name
        self._host = host
        self._port = port
        self._data = PlatformData()
        self._data_buf = PlatformData()
        self._exec_cmd_func = None

    # head:
    # 第一行：标题，是一个固定字符串："Electronic Ecological Estanciero Platform Socket"
    # 第二行：Socket类型，取值为 "Data Socket" 或者 "Cammand Socket"
    # 第三行：平台名称，如："RaspberryPi", 或者 "Windows 7", "Ubuntu 16.04" ...
    # 第四行：设备ID号
    # 第五行：结束标记，固定为"End"
    def _create_head(self, type):
        title = 'Electronic Ecological Estanciero Platform Socket'
        socket_type = ['Data Socket', 'Cammand Socket']
        end = 'end'

        return title + '\n' + socket_type[type] + '\n' + self._name + '\n' + self._id + '\n' + end

    # 第一行：标题，固定字符串："Platform Data"
    # 第二行：温度值：如 "37.5"
    # 第三行：结束标记：固定字符串："End"
    def _create_data(self):
        title = "Platform Data"
        end = "End"

        return title + '\n' + str(self._data.temperature) + '\n' + end

    
    def _connec_socket(self, server_socket, type):
        server_socket.connect((self._host, self._port))
        server_socket.send(self._create_head(type).encode())
        res = server_socket.recv(20).decode()
        if res != 'OK':
            server_socket.close()
            print('链接服务器失败：服务器应答不正确：服务器应答："%s"' % res)
        return True

    def close(self):
        if self._data_socket:
            self._data_socket.close()
            self._data_socket = None
        if self._command_socket:
            self._command_socket.close()
            self._command_socket = None

    def connect_server(self):
        self._data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self._connec_socket(self._data_socket, DataSocket):
            if self._connec_socket(self._command_socket, CommandSocket):
                threading.Thread(target=self._get_cmd, daemon=True).start()
                return True


    def set_temperature(self, temperature): 
        self._data_buf.temperature = temperature

    def upload_data(self):
        if self._data != self._data_buf:
            self._data = self._data_buf.clone()

            if self._data_socket == None:
                print("错误：Data Socket没有连接！")
                return

            try: 
                data = self._create_data().encode()
                self._data_socket.send(data)
                res = self._data_socket.recv(100).decode()
                if res != 'OK':
                    print("数据上传失败：服务器返回：'%s'" % res)
            except BrokenPipeError:
                print("Data Socket 已断开！")
                self._data_socket = None

    def _get_cmd(self):
        while self._command_socket:
            try:
                cmd = self._command_socket.recv(100).decode()
                self._command_socket.send(b'OK')

                print('接收到命令："%s"' % cmd)
                if self._exec_cmd_func:
                    self._exec_cmd_func(cmd)
            except BrokenPipeError:
                print("Cammand Socket 已断开！")
                self._command_socket = None

    def is_connected(self):
        return self._command_socket or self._data_socket

    def set_cmd_func(self, cmd_func):
        self._exec_cmd_func = cmd_func


if __name__ == "__main__":
    import sys

    id = 'mxb-platform'
    name = 'Ubuntu 18.04'
    host = '39.108.3.243'
    port = 51435

    platform_cilent = PlatformClient(id, name, host, port)
    if not platform_cilent.connect_server():
        sys.exit(1)
    print('服务器链接成功！')

    try:
        while platform_cilent.is_connected():
            platform_cilent.set_temperature(37 + random.randint(1, 10) / 10)
            platform_cilent.upload_data()
            time.sleep(1)
        print("服务器已断开！")
    except KeyboardInterrupt:
        platform_cilent.close()
        print('Ctrl-C')
        