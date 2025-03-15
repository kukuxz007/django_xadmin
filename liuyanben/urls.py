from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from .settings import MEDIA_ROOT, MEDIA_URL
from .settings import STATIC_URL, STATIC_ROOT
import xadmin
xadmin.autodiscover()
from xadmin.plugins import xversion
from django.views.generic import RedirectView

xversion.register_models()


urlpatterns = [
    # path('', include('google_indexing.urls')),
    # path('general/', include('general.urls')),
    # path('google_indexing/', include('google_indexing.urls')),
    # path('google_youtube/', include('google_youtube.urls')),
    # path('google_crawl/', include('google_crawl.urls')),
    # path('liuyanben_content/', include('liuyanben_content.urls')),
    re_path(r'^xadmin/', xadmin.site.urls),
    # 添加以下行来将根路由重定向到 xadmin
    re_path(r'^$', RedirectView.as_view(url='/xadmin/', permanent=False), name='index'),
    # path('ueditor/',include('DjangoUeditor.urls')),
    re_path(r'k_media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
    re_path(r'^k_static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),
    # path('__debug2__/', include('debug_toolbar.toolbar')), # debug_toolbar
]

