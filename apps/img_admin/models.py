from django.db import models
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill
from decimal import Decimal
from django.db.models import Sum
from django.contrib.auth.models import AbstractUser, User
import time
import os
import hashlib
from liuyanben import settings
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import TruncMonth
from django.utils import timezone
import calendar
from datetime import datetime


class EditAndDelete(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    status = models.BooleanField(verbose_name='启用', default=True)

    def op_xadmin(self):
        op_list = []
        op_list.append(format_html("""<a href="{}/update/">编辑</a>""", self.id))
        op_list.append(format_html("""<a href="{}/delete/">删除</a>""", self.id))
        return format_html("[" + " | ".join(op_list) + "]")

    op_xadmin.short_description = "操作"

    class Meta:
        abstract = True

class CatLog(EditAndDelete):
    type = models.CharField(
        verbose_name='盲盒类型', 
        null=False, 
        unique=True, 
        blank=False, 
        max_length=200,
        help_text="输入盲盒类型，例如：无限赏、一番赏"
    )
    sort_id = models.IntegerField(verbose_name='排序', null=False, db_index=True, default=0)
    status = models.BooleanField(verbose_name='是否有效', default=True)

    class Meta:
        verbose_name = "盲盒类型"
        verbose_name_plural = "盲盒类型管理"

    def __str__(self):
        return self.type

def get_md5(data):
    return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()


class BlindBoxSeries(EditAndDelete):
    series_name = models.CharField(max_length=255, verbose_name='系列名称', unique=True)
    box_type = models.ForeignKey(CatLog, on_delete=models.CASCADE, verbose_name='盲盒类型')
    cover_image = models.ImageField(upload_to='covers/', verbose_name='系列封面',blank=True, null=True)
    single_draw_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单抽价格')
    sort_id = models.IntegerField(default=0, verbose_name='排序')
    combo_mode = models.BooleanField(default=False, verbose_name='连击模式')
    boss_mode = models.BooleanField(default=False, verbose_name='魔王模式')
    random_drop_mode = models.BooleanField(default=False, verbose_name='随机掉落模式')
    lock_box_mode = models.BooleanField(default=False, verbose_name='锁箱模式')
    status = models.BooleanField(default=True, verbose_name='是否有效')

    class Meta:
        verbose_name = '盲盒系列'
        verbose_name_plural = '盲盒系列管理'

    def __str__(self):
        return "["+str(self.id)+"] "+self.series_name
    
class BlindBox(EditAndDelete):
    LEVEL_CHOICES = [
        ('legendary', '传说'),
        ('diamond', '钻石'),
        ('king', '欧王'),
        ('platinum', '铂金'),
        ('bronze', '青铜'),
        ('normal', '普通'),
    ]
    name = models.CharField(max_length=255, verbose_name='盲盒名称', unique=True)
    series = models.ForeignKey('BlindBoxSeries', on_delete=models.CASCADE, verbose_name='盲盒系列')
    image = models.ImageField(upload_to='blindbox_images/', verbose_name='盲盒图片',blank=True, null=True)
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='参考价格')
    draw_probability = models.IntegerField(verbose_name='万抽概率')  # 确保值小于10000
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='normal', verbose_name='盲盒等级')
    stock = models.IntegerField(verbose_name='库存')
    # combo_mode = models.BooleanField(default=False, verbose_name='连击模式')
    # boss_mode = models.BooleanField(default=False, verbose_name='魔王模式')
    # random_drop_mode = models.BooleanField(default=False, verbose_name='随机掉落模式')
    # lock_box_mode = models.BooleanField(default=False, verbose_name='锁箱模式')
    # sort_id = models.IntegerField(default=0, verbose_name='排序')
    status = models.BooleanField(default=True, verbose_name='是否有效')

    class Meta:
        verbose_name = '盲盒'
        verbose_name_plural = '盲盒'

    def __str__(self):
        return "["+str(self.id)+"] "+self.name
    
class UserData(EditAndDelete):
    openid = models.CharField(max_length=255, verbose_name='OpenID', unique=True)
    nickName = models.CharField(max_length=255, verbose_name='昵称',blank=True, null=True)
    avatarBase64 = models.TextField(verbose_name='头像Base64',blank=True, null=True)
    session_key = models.CharField(max_length=255, verbose_name='会话密钥',blank=True, null=True)
    crystal_value = models.IntegerField(default=0, verbose_name='水晶值',blank=True)
    version= models.IntegerField(default=0, verbose_name='版本号',blank=True)
    

    class Meta:
        verbose_name = '用户数据'
        verbose_name_plural = '用户数据管理'

    def __str__(self):
        return self.openid

class ShippingAddress(EditAndDelete):
    LABEL_CHOICES = [
        ('home', '家'),
        ('company', '公司'),
        ('school', '学校')
    ]
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, verbose_name='用户')
    recipient_name = models.CharField(max_length=255, verbose_name='收货人')
    phone_number = models.CharField(max_length=20, verbose_name='手机号码')
    region = models.CharField(max_length=255, verbose_name='所在地区')
    detailed_address = models.TextField(verbose_name='详细地址')
    label = models.CharField(max_length=50, verbose_name='标签',choices=LABEL_CHOICES, default='home',)
    is_default = models.BooleanField(default=False, verbose_name='是否设为默认地址')

    class Meta:
        verbose_name = '收货地址'
        verbose_name_plural = '收货地址管理'

    def __str__(self):
        return f"{self.recipient_name} - {self.detailed_address}"

class DrawOrder(EditAndDelete):
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, verbose_name='用户')
    series = models.ForeignKey(BlindBoxSeries, on_delete=models.CASCADE, verbose_name='抽奖系列')
    draw_count = models.IntegerField(verbose_name='抽奖次数',default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='抽奖总金额',default=0)
    crystal_deduction = models.IntegerField(verbose_name='抵扣水晶数',default=0)
    winning_details = models.JSONField(verbose_name='中奖详情', blank=True, null=True)

    class Meta:
        verbose_name = '抽奖订单'
        verbose_name_plural = '抽奖订单管理'

    def __str__(self):
        return f"订单{self.id}"

class DrawRecord(EditAndDelete):
    LEVEL_CHOICES = [
        ('legendary', '传说'),
        ('diamond', '钻石'),
        ('king', '欧王'),
        ('platinum', '铂金'),
        ('bronze', '青铜'),
        ('normal', '普通'),
    ]
    draw_order = models.ForeignKey(DrawOrder, on_delete=models.CASCADE, verbose_name='抽奖订单')
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, verbose_name='用户',default=0)
    series = models.ForeignKey(BlindBoxSeries, on_delete=models.CASCADE, verbose_name='盲盒系列',default=0)
    blind_box = models.ForeignKey(BlindBox, on_delete=models.CASCADE, verbose_name='盲盒模型')
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='normal', verbose_name='盲盒等级')
    winning_count = models.IntegerField(verbose_name='中奖数量')
    draw_time = models.DateTimeField(verbose_name='抽奖时间', auto_now_add=True, blank=True, null=True)
    demo = models.TextField(verbose_name='备注', blank=True, null=True)
    status = models.BooleanField(verbose_name='是否有效', default=True)

    class Meta:
        verbose_name = '抽奖记录'
        verbose_name_plural = '抽奖记录管理'