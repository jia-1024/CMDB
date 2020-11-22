from django.urls import path
from assets import views

# 设置namespace的位置
# 用户模板中url反向解析，用于视图函数url反向解析

app_name = 'assets'

urlpatterns = [
    path('report/', views.report, name='report'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('index/', views.index, name='index'),
    path('detail/<int:asset_id>/', views.detail, name="detail"),
    path('', views.dashboard),
]
