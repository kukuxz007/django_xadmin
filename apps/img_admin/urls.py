""" URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.decorators.csrf import csrf_exempt
from django.urls import path
from .views import *
from django.views.decorators.cache import cache_page

cache_timeout = 60 * 60 * 24  # 一天
# cache_timeout = 0  # 不缓存

app_name = "img_admin"
urlpatterns = [
    # path('crawl/<int:keyword_file_id>/', index2, name="index2"),
    # path('crawl_video/<int:keyword_file_id>/', index3, name="index3"),
    # path('export_data/', export_data, name="export_data"),
    # path('init_keys3/<int:id>/', init_keys3, name="init_keys3"),
    # path('', index, name="index"),
    # path('init_url/<int:id>/', init_url, name="init_url"),
    # path('mass_check_api/', mass_check_api, name="mass_check_api"),
    # path('import_cookie_string_file/', import_cookie_string_file, name="import_cookie_string_file"),
    # path('mass_url_update/<int:id>/', mass_url_update, name="mass_url_update"),
    # path('re_mass_url_update/<int:id>/', re_mass_url_update, name="re_mass_url_update"),
    # #path('post_url_all/', post_url_all, name="post_url_all"),
    # path('reset_quota/', reset_quota, name="reset_quota"),
    path('dashboard/', AgentDashboardView.as_view(), name='agent_dashboard'),
]
