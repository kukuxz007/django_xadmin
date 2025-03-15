# from django import forms
# from .models import *
# import hashlib
# from DjangoUeditor.widgets import UEditorWidget
# from DjangoUeditor.models import UEditorField
# import re
# from django.utils.html import format_html
#
#
# def count_words(word):
#     return len(''.join(set(re.compile(r'<[^>]+>', re.S).sub('', word).split(' '))).replace("\n", ""))
#
#
# def get_md5(data):
#     return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()
#
# from django import forms
# from django.core.exceptions import ValidationError
#
#
# class CookieStringForm(forms.ModelForm):
#     def clean(self):
#         cookie_str = self.cleaned_data['cookie_str']
#         md5 = get_md5(cookie_str)
#         if self.has_changed() and CookieString.objects.filter(md5=md5):
#             raise ValidationError(message='重复', code='invalid')
#         return self.cleaned_data
#

