from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cmd', views.cmd, name='cmd'),
    path('image', views.image, name='image'),
    path('index', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('platform-data', views.platform_data, name='platform-data'),
    path('platform-info', views.platform_info, name='platform-info'),
    path('register', views.register, name='register'),
    path('stream', views.stream, name='stream'),
    path('user-info', views.user_info, name='user-info'),
]
