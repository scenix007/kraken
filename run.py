#!/usr/bin/env python
#encoding=utf-8
# Author: Aaron Shao - shao.dut#gmail
# Last modified: 2018-01-23 10:18
# Filename: run.py
# Description: 
import urllib, urllib2 
import json

def get_url(url):
    req = urllib2.Request(url)
    res = urllib2.urlopen(req)
    res = res.read()
    res = json.loads(res)
    return res

def get_html(url):
    req = urllib2.Request(url)
    res = urllib2.urlopen(req)
    res = res.read()
    return res

def get_kraken_price(pair="XETHZEUR", rate=7.843):
    url = "https://api.kraken.com/0/public/Ticker?pair=%s" % pair
    res = get_url(url)
    EUR_price = float(res['result'][pair]['a'][0])
    CNY_price = EUR_price*rate
    return CNY_price



def get_OTC_price(currency = "eth"):
    OTC_URL = "https://otcbtc.com/buy_offers?currency=%s&fiat_currency=cny&payment_type=all" % currency
    html = get_html(OTC_URL)
    start_index =  html.find('<div class="recommend-card__price">') + len('<div class="recommend-card__price">')
    end_index   =  html.find('</div>', start_index)
    html = html[start_index:end_index].replace(',','')
    OTC_price = float(html)
    return OTC_price


def get_huobi_price():
    url = "https://otc.huobi.pro/#/trade/list?coin=3&type=0"
    html = get_html(url)
    start_index =  html.find('3a625218>') + len('3a625218>')
    end_index =  html.find('&nbsp;', start_index)
    html = html[start_index:end_index].replace(',','')
    return float(html)


msg = ""

EURCNY_url = "http://api.k780.com/?app=finance.rate&scur=EUR&tcur=CNY&appkey=10003&sign=b59bc3ef6191eb9f747dd4e83c99f2a4"
EURCNY_rate = 7.848
try:
    res = get_url(EURCNY_url)
    EURCNY_rate =  float(res[u'result'][u'rate'])
except Exception, e:
    print "默认欧元汇率：", EURCNY_rate

print "欧元汇率：", EURCNY_rate


Kraken_price = get_kraken_price("XETHZEUR",EURCNY_rate)
Otc_price = get_OTC_price("eth")
over_rate = Otc_price/(Kraken_price)*100-100
print "ETH:\t%.2f\t%.2f\t%.2f%%" % (Otc_price, Kraken_price, over_rate)

ETHCNY_rate = Kraken_price

msg =  "ETH:%%20%.2f%%20%.2f%%20%.2f%%" % (Otc_price, Kraken_price, over_rate)

Kraken_price = get_kraken_price("EOSETH",ETHCNY_rate)
Otc_price = get_OTC_price("eos")
over_rate_eos = Otc_price/(Kraken_price)*100-100
print "EOS:\t%.2f\t%.2f\t%.2f%%" % (Otc_price, Kraken_price, over_rate_eos)
msg += "%%0aEOS:%%20%.2f%%20%.2f%%20%.2f%%" % (Otc_price, Kraken_price, over_rate_eos)

if over_rate > 5:
    get_html("https://api.telegram.org/bot529838598:AAEnJa-15iE5w13hEy2wSmSGo__qL4ZNj8g/sendMessage?chat_id=227714461&text=%s"%msg)
