import xadmin
from xadmin import views
from xadmin.views import BaseAdminView
from xadmin.plugins import auth
from django.template.response import TemplateResponse
from .models import CatLog,BlindBoxSeries,BlindBox,UserData,ShippingAddress,DrawOrder,DrawRecord
from django.urls import path
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
import csv
from django.http import HttpResponse
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.utils.html import escape
from django.utils.http import urlencode
from xadmin.views import website
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import render
import re
import calendar
from django.utils import timezone
from xadmin.views import CommAdminView
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.conf import settings
from django.utils.html import format_html
from django.db import models


class ReversionEnable(object):
    list_per_page = 100
    relfield_style = 'fa-ajax'
    refresh_times = (3, 5, 10, 60)
    reversion_enable = True
    show_bookmarks = False
    list_display1 = ['id', 'op_xadmin', 'created_at']
    list_editable = ['status']

    def make_enabled(self, request, queryset):
        queryset.update(status=True)
    make_enabled.short_description = "启用"

    def make_disabled(self, request, queryset):
        queryset.update(status=False)
    make_disabled.short_description = "禁用"

@xadmin.sites.register(CatLog)
class CatLogAdmin(ReversionEnable):
    list_display2 = ['type', 'sort_id', 'status_display']
    list_display = tuple(ReversionEnable.list_display1 + list_display2)
    search_fields = ['type']
    list_filter = ['status']
    list_editable = ['status', 'sort_id']

    def status_display(self, obj):
        return "显示" if obj.status else "隐藏"
    status_display.short_description = "状态"

    def save_models(self):
        new_obj = self.new_obj
        if ',' in new_obj.type or '、' in new_obj.type or '|' in new_obj.type:
            # 使用正则表分割输入的字符串
            types = re.split(r'[,、|]', new_obj.type)
            for type_name in types:
                type_name = type_name.strip()
                if type_name:
                    CatLog.objects.create(type=type_name, status=new_obj.status, sort_id=new_obj.sort_id)
        else:
            super().save_models()

    def save_model(self, request, obj, form, change):
        if not change:  # 只在创建新对象时执行批量添加
            types = re.split(r'[,|]', obj.type)
            if len(types) > 1:
                for type_name in types:
                    type_name = type_name.strip()
                    if type_name:
                        CatLog.objects.update_or_create(
                            type=type_name,
                            defaults={'status': obj.status, 'sort_id': obj.sort_id}
                        )
                return  
        super().save_model(request, obj, form, change)


@xadmin.sites.register(BlindBoxSeries)
class BlindBoxSeriesAdmin(ReversionEnable):
    list_display2 = ['series_name', 'image_tag','box_type', 'single_draw_price', 'sort_id', 'status']
    list_display = tuple(ReversionEnable.list_display1 + list_display2)
    list_filter = ['status']
    search_fields = ['series_name', 'box_type']
    def image_tag(self, obj):
        print(obj)
        if obj.cover_image:
            return format_html('<img src="{}" width="50" height="50" />', obj.cover_image.url)
        return "-"
    image_tag.short_description = '图片'

@xadmin.sites.register(BlindBox)
class BlindBoxAdmin(ReversionEnable):
    LEVEL_CHOICES = [
        ('legendary', '传说'),
        ('diamond', '钻石'),
        ('king', '欧王'),
        ('platinum', '铂金'),
        ('bronze', '青铜'),
        ('normal', '普通'),
    ]
    list_display2 = ['name','level','image_tag', 'series', 'reference_price', 'draw_probability']
    list_display = tuple(ReversionEnable.list_display1 + list_display2)
    list_filter = ['status', 'series','level','draw_probability']
    search_fields = ['name']
    actions = ['batch_update_level']
    list_editable = ['level']

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "-"
    image_tag.short_description = '图片'


@xadmin.sites.register(UserData)
class UserDataAdmin(ReversionEnable):
    list_display2 = ['nickName','openid','session_key','crystal_value', 'version','image_tag']
    list_display = tuple(ReversionEnable.list_display1 + list_display2)
    list_filter = ['nickName', 'openid']
    search_fields = ['nickName','openid']
    list_editable = ['crystal_value']

    def image_tag(self, obj):
        if obj.avatarBase64:
            return format_html('<img src="{}" width="50" height="50" />', obj.avatarBase64)
        return "-"
    image_tag.short_description = '头像'

@xadmin.sites.register(ShippingAddress)
class ShippingAddressAdmin(ReversionEnable):
    list_display2 = ['user','recipient_name','phone_number','region', 'detailed_address','is_default']
    list_display = tuple(ReversionEnable.list_display1 + list_display2)
    list_filter = ['user__openid', 'phone_number']
    search_fields = ['user__openid','phone_number','recipient_name']


@xadmin.sites.register(DrawOrder)
class DrawOrderNewAdmin(ReversionEnable):
    list_display2 = ['user','series','draw_count','total_amount', 'crystal_deduction','winning_details']
    list_display = tuple(ReversionEnable.list_display1 + list_display2)
    list_filter = ['user__openid', 'series__series_name']
    search_fields =  ['user__openid', 'series__series_name']
    readonly_fields = ['user','series','draw_count','total_amount', 'crystal_deduction','status','winning_details']

@xadmin.sites.register(DrawRecord)
class DrawRecordAdmin(ReversionEnable):
    list_display2 = ['draw_order','series','user','blind_box','level','winning_count','draw_time']
    list_display = tuple(ReversionEnable.list_display1 + list_display2)
    list_filter = ['user__openid', 'series__series_name','draw_order__id']
    search_fields =  ['user__openid', 'series__series_name']
    readonly_fields = ['draw_order','series','user','blind_box','level','winning_count','draw_time','demo','status']

class GlobalSetting(object):
    site_title = "盲盒管理系统"
    site_footer = "盲盒管理系统"
    menu_style = "accordion"

    def get_site_menu(self):
        user = self.request.user
        if user.is_superuser:
            return [
                {'title': '盲盒类型管理', 'url': self.get_model_url(CatLog, 'changelist'), 'icon': 'fa fa-tags'},
                {'title': '盲盒系列管理', 'url': self.get_model_url(BlindBoxSeries, 'changelist'), 'icon': 'fa fa-tags'},
                {'title': '盲盒数据管理', 'url': self.get_model_url(BlindBox, 'changelist'), 'icon': 'fa fa-tags'},
                {'title': '用户数据管理', 'url': self.get_model_url(UserData, 'changelist'), 'icon': 'fa fa-tags'},
                {'title': '收货地址管理', 'url': self.get_model_url(ShippingAddress, 'changelist'), 'icon': 'fa fa-tags'},
                {'title': '抽奖订单管理', 'url': self.get_model_url(DrawOrder, 'changelist'), 'icon': 'fa fa-tags'},
                {'title': '抽奖记录管理', 'url': self.get_model_url(DrawRecord, 'changelist'), 'icon': 'fa fa-tags'},
                
            ]
        else:
            return []

xadmin.site.register(views.CommAdminView, GlobalSetting)