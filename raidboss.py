#!/usr/bin/python
# -*- coding: utf-8 -*-
#------------------------
#for ドラゴンプロヴィデンス(dmm) autoレイド
#version: 0.1
#Create Date: 01/16/2015
import urllib2
import cookielib
import re
import string
import os
import time

#ドラゴンプロヴィデンス页面操作类
class drapro:
    #レイド救援依頼url匹配
    help_request_re = re.compile(r'a href="(.*?)".*?class="btnImgRaid2 new.*?</a>')
    #未点击レイドboosID匹配
    boss_id_re = re.compile(
        r'<article class="raidList new">[\s\S]*?<a href="http://www.drapro.dmmgames.com/raid/battle_top/(\d+).*?".*?class="btn push-motion0">[\s\S]*?</article>')
    #header
    header = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'
    }
    def __init__(self, cj): 
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    #打开网页的一个封装
    def __openurl(self, url):
        req = urllib2.Request(url, headers = self.header)
        response  = self.opener.open(req)
        page = response.read()
        #print page
        return page.decode("utf-8")

    #打开レイドbossurl，返回レイド救援依頼带new的页面地址，没有找到则为空
    def help_request_url(self, raid_url):
        return self.help_request_re.findall(self.__openurl(raid_url),re.S)
    #得到bossID
    def get_boss_id(self, request_url):
        return self.boss_id_re.findall(self.__openurl(request_url),re.S)
    #打boss
    def beat_boss(self, boss_id_list):
        fileHandle = open('raid_boss.log','a')
        for id in boss_id_list:
            #第一次0bp的url
            msg = self.__openurl(u'http://www.drapro.dmmgames.com/raid/raid_battle_practice/'
                                + id + u'/1/0')
            currenttime = time.strftime('%Y-%m-%d %H:%M:%S',
                                        time.localtime(time.time()))
            print 'time :' + currenttime
            print 'boss_id :' + id
            print msg
            fileHandle.write ('time :'+ str(currenttime) +'\n' 
                            + 'boss_id :' + str(id) + '\n'
                            + str(msg) + '\n')
        fileHandle.close()
    #外部调用的主函数
    def run(self, raid_url = "http://www.drapro.dmmgames.com/raid"):
        hrequest_url = self.help_request_url(raid_url)
        if hrequest_url:
            print hrequest_url
            boss_id = self.get_boss_id(hrequest_url[0])
            if boss_id:
                print boss_id
                self.beat_boss(boss_id)
            else:
                print u'没有新raidboss'
                return
        else:
            print u'没有新raidboss'
            return
#----End of class drapro------------

#网页cookie
def make_cookie(name, value, domain):
    return cookielib.Cookie(
        version=0,
        name=name,
        value=value,
        port=None,
        port_specified=False,
        domain=domain,
        domain_specified=True,
        domain_initial_dot=False,
        path="/",
        path_specified=True,
        secure=False,
        expires=None,
        discard=False,
        comment=None,
        comment_url=None,
         rest=None
    )
#------End of funciton make_cookie------


#程序入口
def main():
    #设置cookie
    cookieurl = "www.drapro.dmmgames.com"
    cookiej = cookielib.CookieJar()
    cookiej.set_cookie(make_cookie("open_id", "12379742", cookieurl))
    cookiej.set_cookie(make_cookie("open_sess_id", 
                              "31a89e11dfe75ea9178724a298a80cf93cfaf11c", 
                               cookieurl))
    cookiej.set_cookie(make_cookie("pc", "1", cookieurl))
    pross = drapro(cj = cookiej)
    while True:
        pross.run()
        time.sleep(100)
#------End of funciton main------


if __name__ == '__main__':
    main()
