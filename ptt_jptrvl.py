#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import json
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pprint import pprint
import psycopg2

DB_HOST = '127.0.0.1'
DB_PORT = '5432'
DB_NAME = 'jptrvl'
DB_USER = 'postgres'
DB_PASS = 'pttjp118'

conn_string = f'host={DB_HOST} user={DB_USER} dbname={DB_NAME} password={DB_PASS} port={DB_PORT}'

options = webdriver.ChromeOptions()
# options.add_argument("--headless")              # 不開啟實體瀏覽器，背景執行
options.add_argument("--start-maximized")  # 最大化視窗 比較好抓 元素不會被隱藏
options.add_argument("--incognito")  # 開啟無痕模式
options.add_argument("--disable-popup-blocking")  # 禁用彈出攔截
options.add_argument("--disable-notifications")  # 取消通知

# service = Service('./chromedriver.exe')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

listData = []


# start_page = 7239
# number = 2
# end_page = start_page - number

def visit():
    for i in range(1):
        url = 'https://www.ptt.cc/bbs/Japan_Travel/index' + str(7239 - i) + '.html'
        driver.get(url)
        sleep(1)
        getListItem()
        getItemDetail()
        saveDb()


def getListItem():
    posts = driver.find_elements(By.CSS_SELECTOR, 'div.r-ent')
    for post in posts:
        try:
            strTitle = post.find_element(By.CSS_SELECTOR, 'div.title > a').get_attribute('innerText')
            strLink = post.find_element(By.CSS_SELECTOR, 'div.title > a').get_attribute('href')
            strAuthor = post.find_element(By.CSS_SELECTOR, 'div.meta > div.author').get_attribute('innerText')
            strPushCount = post.find_element(By.CSS_SELECTOR, 'div.nrec').get_attribute('innerText')

            listData.append({
                "title": strTitle,
                "link": strLink,
                "push_count": strPushCount,
                "author": strAuthor
            })
            sleep(1)

        except NoSuchElementException:
            continue


def getItemDetail():
    for index, articleDict in enumerate(listData):
        driver.get(articleDict['link'])
        meta_lines = driver.find_elements(By.CSS_SELECTOR, 'div.article-metaline')
        strTime = meta_lines[2].find_element(By.CSS_SELECTOR, 'span.article-meta-value').get_attribute('innerText')
        all_text = driver.find_element(By.CSS_SELECTOR, 'div#main-content').get_attribute('innerText')
        pre_text = all_text.split('--')[0]
        texts = pre_text.split('\n')
        contents = texts[4:]
        content = ''.join(contents)

        listData[index]['time'] = strTime
        listData[index]['content'] = content

        sleep(1)

    # pprint(listData)


def saveJson():
    with open("pttjptrvl.json", "w", encoding="utf-8") as fp:
        fp.write(json.dumps(listData, ensure_ascii=False, indent=2))


def saveDb():
    conn = psycopg2.connect(conn_string)
    print("Connect sucessfully!")

    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO public.jptrvl_post(title, link, author, time, push_count, content)
        VALUES (%(title)s, %(link)s, %(author)s, %(time)s, %(push_count)s, %(content)s);
    ''', {'title': listData['title'], 'link': listData['link'], 'author': listData['author'], 'time': listData['time'],
          'push_count': listData['push_count'], 'content': listData['content']})

    print(f'[{listData["title"]}] Append sucessfully')

    conn.commit()

    cursor.close()
    conn.close()


def close():
    driver.quit()


if __name__ == '__main__':
    visit()
    # saveJson()
    close()
