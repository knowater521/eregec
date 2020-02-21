# config.py
# 项目配置


import os as _os
from django.conf import settings as _settings


# 用户数据文件目录
user_data_dir = _os.path.join(_settings.BASE_DIR, "data/user")

# 服务器监听范围
platform_socket_bind_ip = '0.0.0.0'

# 平台端socket的监听端口
platform_socket_port = 51436

# 平台端socket最大监听数
platform_socket_max_listen = 50