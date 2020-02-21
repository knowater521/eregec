# 运行服务器

1. 通过Django自带的测试服务器运行：
```shell
python3 manage.py runserver 0.0.0.0:端口
```

2. 通过Nginx+UWSGI运行（推荐）  
安装Nginx：
```shell
sudo apt install nginx
```
安装Python的UWSGI库
```shell
pip3 install uwsgi
```