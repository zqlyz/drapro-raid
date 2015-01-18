#!/usr/bin/python
# -*- coding: utf-8 -*-
#------------------------
#for ドラゴンプロヴィデンス(dmm) autoレイド
#version: 0.2
#已实现功能：实现自动探索area，自动打raidboss（自己和他人都可以）
#缺陷：自己打不过的boss不能救援请求，cookie失效后脚本就无用
#代码：编码不整洁，混乱
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
    help_request_re = re.compile(
        r'<a href="(.*?)".*?class="btnImgRaid2 new.*?</a>')
    #未点击他人的レイドboosID匹配
    other_boss_id_re = re.compile(
        r'<article class="raidList new">[\s\S]*?battle_top/(\d+).*?"')

    #自己的レイドbossID匹配
    self_boss_id_re = re.compile(r'<a href=".*?/battle_top/(\d+).*?</a>')

    #自己レイドboss url
    self_boss_url_re = re.compile(r'<a href="(.*?/battle_top/.*?)".*?</a>')

    #探索选择的stage匹配
    stage_4_re = re.compile(
        r'<a href="(.*?quest_exec/5.*?)".*?class="btnMR push-motion0">')

    #用于判断是否是出现areaboss
    area_boss_re = re.compile(
        r'<a href="(.*?boss_battle_flash/5.*?)" class="btnLR push-motion0">')

    #area重开时需要第二次匹配url
    area_again_re = re.compile(
        r'var nextUrl = "(http:/.*?/quest_exec/5.*?)";')

    #保存已打了自己的raidboss的次数
    self_boss_beat_times = 0

    #header
    header = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 \
                    (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'
    }
    def __init__(self, cj): 
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    #打开网页的一个封装
    def __openurl(self, url):
        req = urllib2.Request(url, headers = self.header)
        try:
            response  = self.opener.open(req)
        except httplib.BadStatusLine,e:
            print 'httplib.BadStatusLine error'
        page = response.read()
        #print page
        return page.decode("utf-8")

    #打开レイドbossurl，返回自己raidbossID和レイド救援依頼带new的页面地址
    def help_request_url(self, raid_url):
        page = self.__openurl(raid_url)
        self_boss_id = self.self_boss_id_re.findall(page, re.S)
        
        if not self_boss_id:
            self_boss_beat_times = 0
        print 'self_boss_id :' + str(self_boss_id)
        return self_boss_id ,self.help_request_re.findall(page, re.S)

    #得到bossID
    def get_boss_id(self, request_url):
        return self.other_boss_id_re.findall(self.__openurl(request_url), re.S)

    #打其他人的boss
    def beat_other_boss(self, other_boss_id_list):
        for id in other_boss_id_list:
            self.beat_boss(id)

    #打自己的boss
    def beat_self_boss(self, self_boss_id):
        if self_boss_id:
            #在1,3,5次打（即打了0,2,4次的时候）的时候用一倍攻击其余时候用三倍攻击
            if not (self.self_boss_beat_times % 2):
                self.beat_boss(self_boss_id)
            else:
                self.beat_boss(self_boss_id, '3')
            self.self_boss_beat_times += 1

    #打boss, method = "1"免费, method = "2"一倍攻击，method = "3"三倍攻击
    def beat_boss(self, boss_id, method = '1'):
        #fileHandle = open('raid_boss.log','a')
        #第一次0bp的url
        msg = self.__openurl(
            u'http://www.drapro.dmmgames.com/raid/raid_battle_practice/'
            + boss_id.decode() + u'/' + method.decode() + u'/0')
        currenttime = time.strftime('%Y-%m-%d %H:%M:%S',
                                     time.localtime(time.time()))
        print 'time :' + currenttime
        print 'boss_id :' + boss_id
        print msg
        #fileHandle.write ('time :'+ str(currenttime) +'\n' 
        #                + 'boss_id :' + str(boss_id) + '\n'
        #                + str(msg) + '\n')
        #fileHandle.close()

    #外部调用的主函数
    def run(self, raid_url = "http://www.drapro.dmmgames.com/raid"):
        self_boss_id, hrequest_url = self.help_request_url(raid_url)
        if self_boss_id:
            self.beat_self_boss(self_boss_id[0])
        if hrequest_url:
            print hrequest_url
            boss_id = self.get_boss_id(hrequest_url[0])
            if boss_id:
                self.beat_other_boss(boss_id)
            else:
                print u'没有新raidboss'
                return
        else:
            print u'没有新raidboss'
            return

    #自动探索
    def test(self, url = "http://www.drapro.dmmgames.com/quest"):
        stage_url = self.stage_4_re.findall(self.__openurl(url), re.S)
        print stage_url
        result_page = self.__openurl(stage_url[0])
        area_boss_url = self.area_boss_re.findall(result_page, re.S)
        area_again_url = self.area_again_re.findall(result_page, re.S)
        print 'area_boss_url :' + str(area_boss_url)
        print 'area_again_url :' + str(area_again_url)
        if area_boss_url:
            #self.__openurl(area_boss_url[0] + u'&play=1')
            req = urllib2.Request(area_boss_url[0] + u'&play=1', headers = self.header)
            response  = self.opener.open(req)
        if area_again_url:
            req = urllib2.Request(area_again_url[0], headers = self.header)
            response  = self.opener.open(req)

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
                              "939dc26712a6d5b7e6a51c3502b290b9f6dbc2ee", 
                               cookieurl))
    cookiej.set_cookie(make_cookie("pc", "1", cookieurl))
    pross = drapro(cj = cookiej)
    count = 0
    while True:
        pross.run()
        if not (count % 5):
            count = 0
            pross.test()
        count += 1
        time.sleep(100)
#------End of funciton main------


if __name__ == '__main__':
    main()
