#!/usr/bin/env python3
# coding: utf-8

from bs4 import BeautifulSoup as bs
import requests as req
import json
from pprint import pprint
from time import sleep
from random import uniform
import sqlalchemy as db
from sqlalchemy import exc

my_headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

url = 'https://historical.findrate.tw/his.php?c=JPY'

listData = []

def getMainData():
    res = req.get(url= url, headers=my_headers)
    soup = bs(res.text, "lxml")


def getDetailData():
    pass

def saveJson():
    with open("pttjptrvl_bs.json", "w", encoding="utf-8") as fp:
        fp.write(json.dumps(listData, ensure_ascii=False, indent=2))

# if __name__ == '__main__':
    