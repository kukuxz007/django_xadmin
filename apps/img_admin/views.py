# from django.http import HttpResponse
# from .models import *
# from general.multi import Multi, get_md5, walkdir, get_connector
# import os
# import asyncio
# import aiohttp
# from django.db.models import Q
# import time
#
# app_name = EditAndDelete._meta.app_label
#
#
# def index(request):
#     pid = os.getpid()
#     x0 = CookieString.objects.raw(
#         "select id,sum(times) as keyword_num  from google_indexing_cookiestring  where status=1")
#     keyword_num = x0[0].keyword_num
#     if keyword_num == None:
#         keyword_num = 0
#     x2 = CookieString.objects.raw(
#         "select id,count(id) as keyword_num2  from google_indexing_cookiestring  where status=1")
#     keyword_num2 = 200 * x2[0].keyword_num2
#     print(keyword_num2)
#     print(keyword_num)
#     used_num = keyword_num2 - keyword_num
#
#     html = """
#         当前进程: {pid}<br />
#         总额度: {keyword_num2}<br />
#         已用额度: {used_num}<br />
#         剩余额度:{keyword_num}<br />
#         """.format(pid=pid, keyword_num=keyword_num, used_num=used_num, keyword_num2=keyword_num2)
#     return HttpResponse(html)
#
#
# def reset_quota(request):
#     CookieString.objects.all().update(times=200)
#     return HttpResponse("推送额度已重置")
#
#
# def init_url(request, id):
#     t2 = time.time()
#     files_list = Task.objects.get(id=id)
#     url_list = files_list.url_list
#     url_list_file = os.path.join("media", str(url_list))
#     with open(url_list_file, encoding='utf-8') as e:
#         url_list_new = e.read().split("\n")
#     Keywords_list = []
#     for i in url_list_new:
#         Keywords_list.append(TaskItem(url=i, url_list_id=id, cookie_str=""))
#     TaskItem.objects.bulk_create(Keywords_list, ignore_conflicts=True)
#     x = "耗时:" + str(int(time.time() - t2))
#     return HttpResponse("待推送网址列表已生成<br />" + x)
#
#
# def import_cookie_string_file(request):
#     file_list = walkdir(os.path.join("media", "index_api"))
#     bluk_list = []
#     for i in file_list:
#         print(i)
#         with open(os.path.join(i), encoding='utf-8') as e:
#             url_list = e.read().strip().split("\n")
#             for j in url_list:
#                 print(j)
#                 j_list = j.split("||")
#                 cookie_str = j_list[0].strip()
#                 project = j_list[1].strip()
#                 email = j_list[2].strip()
#                 md5 = get_md5(cookie_str + email)
#                 if len(j) > 0:
#                     bluk_list.append(
#                         CookieString(email=email, cookie_str=cookie_str, md5=md5, project=project, status=False))
#                 # break
#     CookieString.objects.bulk_create(bluk_list, ignore_conflicts=True)
#     return HttpResponse("导入google indexing文件成功")
#
#
# async def single_check_api(pool, keywords_list_item, proxy_list, timeout, insert_data, update_data):
#     import random
#     from urllib.parse import urlparse, quote
#     import urllib
#     # print(urllib.quote("OhlUfWQlI_1HdW0XJdm6hdBo"))
#     id = keywords_list_item["id"]
#     cookie_str = keywords_list_item["cookie_str"].strip()
#     # print(cookie_str)
#     # project = keywords_list_item["project"]
#     # email = keywords_list_item["email"]
#     conn = pool.connection()
#     cursor = conn.cursor()
#     # proxy_list = ['socks5://127.0.0.1:7080']
#     connector = get_connector(proxy_list)
#     try:
#         async with aiohttp.ClientSession(connector=connector) as session:
#             url = "https://www.googleapis.com/oauth2/v4/token"
#             headers = {"Host": "www.googleapis.com", "Content-Type": "application/x-www-form-urlencoded"}
#             async with session.post(url, data=cookie_str, ssl=False, timeout=timeout, headers=headers) as response:
#                 content = await response.json()
#                 print(content)
#                 if "access_token" in content:
#                     sql = "update {update_data} set status=TRUE where id=%s".format(update_data=update_data)
#                     cursor.execute(sql, (id))
#                     conn.commit()
#                     links = [content, 'success']
#                 else:
#                     sql = "update {update_data} set status=FALSE where id=%s".format(update_data=update_data)
#                     cursor.execute(sql, (id))
#                     conn.commit()
#                     links = [content, 'unknown']
#     except Exception as e:
#         print(e.args)
#         # time2 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#         sql = "update {update_data} set status=FALSE where id=%s".format(update_data=update_data)
#         cursor.execute(sql, (id))
#         conn.commit()
#         links = ["22", 'error']
#     cursor.close()
#     conn.close()
#     return links
#
#
# def mass_check_api(request):
#     action_name = "批量验证api是否可用<br />\n"
#     t2 = time.time()
#     proxy_list = Multi().get_proxy_list()
#     keywords_all = CookieString.objects.filter(status=False).values('id', 'cookie_str', 'project',
#                                                                     'email')
#     links = []
#     for i in keywords_all:
#         links.append(i)
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     semaphore_num = 50
#     timeout = 60
#     update_data = "	google_indexing_cookiestring"
#     insert_data = "google_indexing_cookiestring"
#     loop.run_until_complete(Multi().main(semaphore_num, single_check_api, links, proxy_list, timeout,
#                                          insert_data, update_data))
#     x = "耗时:" + str(int(time.time() - t2))
#     return HttpResponse(action_name + x)
#
#
# async def get_google_token(proxy_list, cookie_str):
#     # print("xxx", cookie_str)
#     connector = get_connector(proxy_list)
#     url = "https://www.googleapis.com/oauth2/v4/token"
#     # cookie_str = urllib.parse.quote(cookie_str)
#     headers = {"Host": "www.googleapis.com", "Content-Type": "application/x-www-form-urlencoded"}
#     try:
#         async with aiohttp.ClientSession(connector=connector) as session:
#             async with session.post(url, data=cookie_str, ssl=False, headers=headers) as response:
#                 content = await response.json()
#                 return content["access_token"]
#     except Exception as e:
#         print(e.args)
#         return ""
#
#
# async def single_url_update(pool, keywords_list_item, proxy_list, timeout, insert_data, update_data):
#     to_url = keywords_list_item["url"]
#     to_id = keywords_list_item["id"]
#     conn = pool.connection()
#     cursor = conn.cursor()
#     connector = get_connector(proxy_list)
#     email_list = ['kukuxz007@gmail.com', 'hcy0426@gmail.com', 'hcy0426@gmail.com', 'ho920fr@gmail.com', 'ho920fr@gmail.com', 'bhowl.dign@gmail.com', 'bhowl.dign@gmail.com', 'hi1031@gmail.com', 'hi1031@gmail.com', 'th920tr@gmail.com', 'th920tr@gmail.com', 'ty10der15@gmail.com', 'ty10der15@gmail.com', 'yu32132149a@gmail.com', 'yu32132149a@gmail.com', 'ty920ta@gmail.com', 'ty920ta@gmail.com', 'sq0202@gmail.com', 'sq0202@gmail.com', 'dt920fa@gmail.com', 'dt920fa@gmail.com', 'hcy0731@gmail.com', 'hcy0731@gmail.com', 'th1008ter@gmail.com', 'th1008ter@gmail.com', 'sq0606@gmail.com', 'sq0606@gmail.com', 'ldyui00a111@gmail.com', 'ldyui00a111@gmail.com', 'y321i432ak@gmail.com', 'y321i432ak@gmail.com', 'hcy0707@gmail.com', 'hcy0707@gmail.com', 'yu0901rt@gmail.com', 'yu0901rt@gmail.com', 'ty1010ther@gmail.com', 'ty1010ther@gmail.com', 'abramlaylahsgdn@gmail.com', 'abramlaylahsgdn@gmail.com', 'sq0505@gmail.com', 'sq0505@gmail.com', 'bniejg.kdfj@gmail.com', 'bniejg.kdfj@gmail.com', 'hk1010ty@gmail.com', 'hk1010ty@gmail.com']
#     email_list2 = ["'"+i+"'" for i in email_list]
#     email_list2_str = ','.join(email_list2)
#     #print(email_list2_str)
#     sql = "select `id`,`cookie_str` from google_indexing_cookiestring where times>0 and email in ({email_list2_str}) and status=1 order by rand() limit 1".format(email_list2_str=email_list2_str)
#     #print(sql)
#     cursor.execute(sql)
#     proxy_str = cursor.fetchone()
#     if proxy_str:
#         sql1 = "update google_indexing_cookiestring set times=times-1 where id=%s"
#         cursor.execute(sql1, (proxy_str[0]))
#         conn.commit()
#         cookie_str = proxy_str[1].strip()
#         # print(cookie_str)
#         access_token = await get_google_token(proxy_list, cookie_str)
#         url = "https://indexing.googleapis.com/v3/urlNotifications:publish"
#         headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json;charset=UTF-8"}
#         json_content = {"url": to_url, "type": "URL_UPDATED"}
#         try:
#             async with aiohttp.ClientSession(connector=connector) as session:
#                 async with session.post(url, json=json_content, ssl=False, headers=headers) as response:
#                     content = await response.json()
#                     now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#                     if "error" not in content:
#                         print(content)
#                         is_post = 1
#                         sql = "update {update_data} set is_post=1,cookie_str=%s,updated_at=%s where id=%s".format(
#                             update_data=update_data)
#                         cursor.execute(sql, (cookie_str, now_time, to_id))
#                         conn.commit()
#                     else:
#                         print(content)
#                         is_post = 2
#                         sql = "update {update_data} set is_post=2,updated_at=%s where id=%s".format(
#                             update_data=update_data)
#                         cursor.execute(sql, (now_time, to_id))
#                         conn.commit()
#         except Exception as e:
#             print(e.args)
#             is_post = 2
#     else:
#         is_post = 2
#     cursor.close()
#     conn.close()
#     return [to_url, is_post]
#
#
# def mass_url_update(request, id):
#     x = Task.objects.filter(id=id).values('semaphore_num')
#     semaphore_num = x[0]["semaphore_num"]
#     """
#     获取总提交额度sum_times
#     """
#     y = CookieString.objects.raw(
#         "select id,sum(times) as sum_times from google_indexing_cookiestring where times>0 and status=1")
#     sum_times = y[0].sum_times
#     """
#     获取需提交索引数sum_times2
#     """
#     keywords_all = TaskItem.objects.filter(url_list_id=id).filter(~Q(is_post=1)).values('url', 'id')
#     keywords_list = []
#     for i in keywords_all:
#         keywords_list.append(i)
#     sum_times2 = len(keywords_list)
#     t2 = time.time()
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     print("剩余额度:", sum_times, "需要提交索引数:", sum_times2)
#     proxy_list = Multi().get_proxy_list()
#     timeout = 60
#     update_data = "	google_indexing_taskitem"
#     insert_data = "google_indexing_taskitem"
#     if sum_times == None:
#         x = "已经没有额度"
#     elif sum_times2 == 0:
#         x = "已搜刮结束"
#     else:
#         loop.run_until_complete(Multi().main(semaphore_num, single_url_update, keywords_list, proxy_list, timeout,
#                                              insert_data, update_data))
#         x = "消耗:" + str(int(time.time() - t2))
#     return HttpResponse(x)
#
#
# def re_mass_url_update(request, id):
#     for i in range(1, 5):
#         TaskItem.objects.filter(url_list_id=id).all().update(is_post=0)
#         mass_url_update(request, id)
#         return HttpResponse("已完成")
#
#
# from django.views.generic import TemplateView
# from django.contrib.auth.mixins import LoginRequiredMixin
# from .models import Agent, SalesRecord
# from django.db.models import Sum
# from decimal import Decimal
#
# class AgentDashboardView(LoginRequiredMixin, TemplateView):
#     template_name = 'agent_dashboard.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         agent = self.request.user
#         
#         # 获取代理商自己的销售业绩和佣金
#         sales = SalesRecord.objects.filter(agent=agent)
#         total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
#         first_level_commission, second_level_commission = agent.calculate_commission()
#         
#         # 获取直推代理商的业绩
#         direct_referrals_performance = agent.get_direct_referrals_performance()
#
#         context.update({
#             'agent': agent,
#             'total_sales': total_sales,
#             'first_level_commission': first_level_commission,
#             'second_level_commission': second_level_commission,
#             'direct_referrals_performance': direct_referrals_performance,
#         })
#         return context