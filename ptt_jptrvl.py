#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import json
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

options = webdriver.ChromeOptions()
# options.add_argument("--headless")              # 不開啟實體瀏覽器，背景執行
options.add_argument("--start-maximized")  # 最大化視窗 比較好抓 元素不會被隱藏
options.add_argument("--incognito")  # 開啟無痕模式
options.add_argument("--disable-popup-blocking")  # 禁用彈出攔截
options.add_argument("--disable-notifications")  # 取消通知

service = Service('./chromedriver.exe')

driver = webdriver.Chrome(
    options=options,
    service=service
)

listData = []


def visit():
    driver.get('https://www.ptt.cc/bbs/Japan_Travel/index.html')
    sleep(1)


def getListItem():
    posts = driver.find_elements(By.CSS_SELECTOR, 'div.r-ent')
    for post in posts:
        strTitle = post.find_element(By.CSS_SELECTOR, 'div.title > a').get_attribute('innerText')
        strLink = post.find_element(By.CSS_SELECTOR, 'div.title > a').get_attribute('href')
        strAuthor = post.find_element(By.CSS_SELECTOR, 'div.meta > div.author').get_attribute('innerText')
        strPushCount = "no pushs"
        #         if post.find_element(By.CSS_SELECTOR, 'div.nrec span') != None:
        #             strPushCount = post.find_element(By.CSS_SELECTOR, 'div.nrec span').get_attribute('innerText')
        #         else:
        #             continue

        listData.append({
            "title": strTitle,
            "link": strLink,
            "push_count": strPushCount,
            "author": strAuthor
        })
        sleep(1)


def getItemDetail():
    for index, articleDict in enumerate(listData):
        driver.get(articleDict['link'])
        meta_lines = driver.find_elements(By.CSS_SELECTOR, 'div.article-metaline')
        strTime = meta_lines[2].find_element(By.CSS_SELECTOR, 'span.article-meta-value').get_attribute('innerText')
        strContent = driver.find_element(By.CSS_SELECTOR, 'div#main-content').text
        listData[index]['time'] = strTime
        listData[index]['content'] = strContent

        sleep(1)

    print(listData)


def saveJson():
    pass


def saveDb():
    pass


def close():
    driver.quit()


if __name__ == '__main__':
    visit()
    getListItem()
    getItemDetail()
    close()
