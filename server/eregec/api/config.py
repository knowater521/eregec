# config.py
# 项目配置


import os
from django.conf import settings


# 用户数据文件目录
user_data_dir = os.path.join(settings.BASE_DIR, "data/user")

# 平台端socket的监听端口
platform_socket_port = 51435

# 平台端socket最大监听数
platform_socket_max_listen = 50