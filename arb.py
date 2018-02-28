#!/usr/bin/env python
#encoding=utf-8
# Author: Aaron Shao - shao.dut#gmail
# Last modified: 2018-02-08 14:01
# Filename: arb.py
# Description:  huobi & kraken 套利机会发现

import urllib, urllib2 
import json
import datetime
import sys

def get_url(url, with_header = False):
    req = urllib2.Request(url)
    if with_header:
        req.add_header("Accept", "application/json, text/plain, */*")
        req.add_header("Accept-Language", "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4")
        req.add_header("Cache-Control", "no-cache")
        req.add_header("Connection", "keep-alive")
        req.add_header("Cookie", "__jsluid=54dfdf9396cd1a90fa46cc5fc2cc81c0; gr_user_id=d2f1957f-0124-4587-bd73-7ce176b0ab19; acw_tc=AQAAAHzQiVN0XA4AfPdUcoXfYXjGPaCA; __cfduid=d608b6ef40021eb162262c74234697c541518100732; _ga=GA1.2.829381328.1516711598; _gid=GA1.2.195001734.1518098691; __zlcmid=kch4FrQGctsSXA; 818dfed477ddd24a_gr_session_id=06e96dd3-5b8e-4610-969c-711ed34fbcf9")
        req.add_header("fingerprint", "b2b0badcf280430aac9dc3b0ad451eb5")
        req.add_header("Host", "api-otc.huobi.pro")
        req.add_header("Origin", "https://otc.huobi.pro")
        req.add_header("otc-language", "zh-CN")
        req.add_header("Pragma", "no-cache")
        req.add_header("Referer", "https://otc.huobi.pro/")
        req.add_header("token", "TICKET_709ea1b4d410cdf3ac77465579fd3f070af86bfe91004a23a23dbf68334174d6")
        req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36")
        req.add_header("X-Requested-With", "XMLHttpRequest")


    res = urllib2.urlopen(req)
    res = res.read()
    res = json.loads(res)
    return res

def get_html(url):
    req = urllib2.Request(url)
    res = urllib2.urlopen(req)
    res = res.read()
    return res

def get_EURCNY_rate():
    EURCNY_url = "http://api.k780.com/?app=finance.rate&scur=EUR&tcur=CNY&appkey=10003&sign=b59bc3ef6191eb9f747dd4e83c99f2a4"
    EURCNY_rate = 7.848
    update_time = datetime.datetime(1990,1,1)
    try:
        items = file('EURCNY.cache').read().split('\t')
        update_time = datetime.datetime.strptime(items[0], "%Y%m%d-%H:%M")
        EURCNY_rate = float(items[1])
    except Exception ,e:
        print >> sys.stderr, "Exception: ",e , ". Using default EURCNY_rate = 7.848"

    if (datetime.datetime.now() - update_time).seconds > 600:
        try:
            res = get_url(EURCNY_url)
            EURCNY_rate =  float(res[u'result'][u'rate'])
            update_time = datetime.datetime.now()
        except Exception, e:
            print >> sys.stderr, "Exception: ",e , ". Using default EURCNY_rate = 7.848"

    try:
        with open("EURCNY.cache", 'w') as f_out:
            f_out.write("%s\t%f" % (update_time.strftime("%Y%m%d-%H:%M"), EURCNY_rate))
    except Exception ,e:
        print >> sys.stderr, "Exception: ",e , ". Write cache file failed."
    return EURCNY_rate, update_time



def get_kraken_price(pair="XETHZEUR", rate=7.843):
    rate, update_time = get_EURCNY_rate()
    url = "https://api.kraken.com/0/public/Ticker?pair=%s" % pair
    res = get_url(url)
    bid_price = float(res['result'][pair]['b'][0]) * rate
    ask_price = float(res['result'][pair]['a'][0]) * rate
    return bid_price, ask_price

def get_huobi_price():
    sell_url = "https://api-otc.huobi.pro/v1/otc/trade/list/public?coinId=3&tradeType=0&currentPage=1&payWay=&country=&merchant=1&online=1&range=1&currPage=1"
    buy_url = "https://api-otc.huobi.pro/v1/otc/trade/list/public?coinId=3&tradeType=1&currentPage=1&payWay=&country=&merchant=1&online=1&range=1&currPage=1"
    res = get_url(sell_url, with_header = True)
    bid_price = float(res['data'][0]["price"])
    res = get_url(buy_url, with_header = True)
    ask_price = float(res['data'][0]["price"])

    return bid_price, ask_price

k_b, k_a = get_kraken_price()
h_b, h_a = get_huobi_price()

over_rate = ( 100 * h_b / k_a) - 100

with open("result.txt", "a") as f_out:
    f_out.write("%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f%%\n" % \
            (datetime.datetime.now().strftime("%Y%m%d-%H:%M"), k_b, k_a, h_b, h_a, over_rate))


# alert 财神

if over_rate > 4.4:
    msg =  "ETH:%%20%.2f%%20%.2f%%20%.2f%%" % (h_b, k_a, over_rate)
    get_html("https://api.telegram.org/bot529838598:AAEnJa-15iE5w13hEy2wSmSGo__qL4ZNj8g/sendMessage?chat_id=227714461&text=%s"%msg)
