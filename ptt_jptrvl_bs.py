#!/usr/bin/env python3
# coding: utf-8

from bs4 import BeautifulSoup
import requests as req
import json

my_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

listData = []

# url = 'https://www.ptt.cc/bbs/Japan_Travel/index'+str(7296-i)+'.html'

domainName = 'https://www.ptt.cc/bbs/Japan_Travel/index'

pages = 1

def getMainData():
    for page in range(7295, pages + 1):
        res = req.get(url = domainName + str(page) + '.html', headers = my_headers)
        print(res.text)
        #soup = BeautifulSoup(res.text, "lxml")

if __name__ == '__main__':
    getMainData()