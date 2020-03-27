# config.py
# 项目配置

import os as _os

# 服务器监听范围
platform_socket_bind_ip = '0.0.0.0'

# 平台端socket的监听端口
platform_socket_port = 51435

# 平台端socket最大监听数
platform_socket_max_listen = 50

# SQLite3数据库文件
sqlite3_database_file = 'db.sqlite3'