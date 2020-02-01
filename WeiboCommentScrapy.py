# -*- coding: utf-8 -*-
import requests

requests.packages.urllib3.disable_warnings()

from lxml import etree

from datetime import datetime, timedelta

from threading import Thread

import csv

from math import ceil

import os

import re
from time import sleep
from random import randint

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Cookie': '''_T_WM=81457129498; ALF=1583072585; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhhcPq.p4_gg2nxPxSEfVIc5JpX5K-hUgL.Fo27ehMRSK.pSKz2dJLoI0qLxKnL1K2LBK2LxKnL1K5L1hBLxK-LBK-LB.BLxK-LBKBLBKMLxKBLBonL1h5LxK.LBKzL1KMt; MLOGIN=1; SCF=AuldYKL41nt-bS9piskZbRIz3RH-vSJ77gL5-4H3Fwfa6L8J4Zeq_EgRmRt-JNr5gl_tr_xz2E6KlkwcRdcfGkc.; SUB=_2A25zMEi9DeRhGedO61UZ9SfNzj6IHXVQ22j1rDV6PUJbktAKLXHFkW1NJodAs0vpOpUQBFjs4GO7jG4kDQ1q7Y3x; SUHB=0Elc_n9raiUw6n; SSOLoginState=1580480749'''
}

class WeiboCommentScrapy(Thread):

    def __init__(self,wid):
        global headers
        Thread.__init__(self)
        self.headers = headers

        if not os.path.exists('comment'):
            os.mkdir('comment')
        self.wid = wid
        self.start()

    def parse_time(self,publish_time):
        publish_time = publish_time.split('来自')[0]
        if '刚刚' in publish_time:
            publish_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        elif '分钟' in publish_time:
            minute = publish_time[:publish_time.find('分钟')]
            minute = timedelta(minutes=int(minute))
            publish_time = (datetime.now() -
                            minute).strftime('%Y-%m-%d %H:%M')
        elif '今天' in publish_time:
            today = datetime.now().strftime('%Y-%m-%d')
            time = publish_time[3:]
            publish_time = today + ' ' + time
        elif '月' in publish_time:
            year = datetime.now().strftime('%Y')
            month = publish_time[0:2]
            day = publish_time[3:5]
            time = publish_time[7:12]
            publish_time = year + '-' + month + '-' + day + ' ' + time
        else:
            publish_time = publish_time[:16]
        return publish_time

    def get_one_comment_struct(self,comment):
        # xpath 中下标从 1 开始
        userURL = "https://weibo.cn/{}".format(comment.xpath(".//a[1]/@href")[0])

        content = comment.xpath(".//span[@class='ctt']/text()")
        # '回复' 或者只 @ 人
        if '回复' in content or len(content)==0:
            test = comment.xpath(".//span[@class='ctt']")
            content = test[0].xpath('string(.)').strip()

            # 以表情包开头造成的 content == 0,文字没有被子标签包裹
            if len(content)==0:
                content = comment.xpath('string(.)').strip()
                content = content[content.index(':')+1:]
        else:
            content = content[0]


        return content

    def write_to_csv(self,result,isHeader=False):
        with open('comment/' + self.wid + '.csv', 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            if isHeader == True:
                writer.writerows([self.result_headers])
            writer.writerows(result)
        print('已成功将{}条评论写入{}中'.format(len(result),'comment/' + self.wid + '.csv'))

    def run(self):

        res = requests.get('https://weibo.cn/comment/{}'.format(self.wid).encode("utf-8").decode("latin-1"),headers=self.headers,verify=False)
        commentNum = re.findall("评论\[.*?\]",res.text)[0]
        commentNum = int(commentNum[3:len(commentNum)-1])
        print(commentNum)
        pageNum = ceil(commentNum/10)
        print(pageNum)
        result = []
        for page in range(1):


            res = requests.get('https://weibo.cn/comment/{}?page={}'.format(self.wid,page+1), headers=self.headers,verify=False)

            html = etree.HTML(res.text.encode('utf-8'))

            comments = html.xpath("/html/body/div[starts-with(@id,'C')]")

            print('第{}/{}页'.format(page+1,pageNum))

            for i in range(len(comments)):
                temp = self.get_one_comment_struct(comments[i])
                if ("\xa0举报" in temp or "//" in temp or "回复" in temp): # 某些莫名评论会出现，清除
                    continue
                result.append(self.get_one_comment_struct(comments[i]))

            sleep(randint(1,5)) # prevent got ban by the server
        print(result)
        f = open("save/" + self.wid + '.txt', 'w')
        for ele in result:
            print(ele)
            ele = ele + "\n"
            f.writelines(ele)
        f.close()
        return result

if __name__ =="__main__":
    result = WeiboCommentScrapy(wid='Is4bIu4ZR')


