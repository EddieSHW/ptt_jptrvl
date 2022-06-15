#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from time import sleep
import json
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pprint import pprint
import psycopg2
# import psycopg2.extras
from psycopg2.extras import execute_values

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


# start_page = 7240
# pages = 2

def visit():
    for i in range(1):
        url = 'https://www.ptt.cc/bbs/Japan_Travel/index' + str(7192 - i) + '.html'
        driver.get(url)
        sleep(1)
        getListItem()
        getItemDetail()


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
        if len(meta_lines) == 3:
            strTime = meta_lines[2].find_element(By.CSS_SELECTOR, 'span.article-meta-value').get_attribute('innerText')
            all_text = driver.find_element(By.CSS_SELECTOR, 'div#main-content').get_attribute('innerText')
            pre_text = all_text.split('--')[0]
            texts = pre_text.split('\n')
            contents = texts[4:]
            content = ''.join(contents)

            listData[index]['publish_time'] = strTime
            listData[index]['content'] = content

            sleep(1)

        else:
            listData[index]['publish_time'] = None
            listData[index]['content'] = None

    #     pprint(listData)
    savepgDb()
    listData.clear()


def saveJson():
    with open("pttjptrvl.json", "w", encoding="utf-8") as fp:
        fp.write(json.dumps(listData, ensure_ascii=False, indent=2))


def savepgDb():
    conn = psycopg2.connect(conn_string)
    print("Connect sucessfully!")
    try:

        cursor = conn.cursor()  # cursor_factory=psycopg2.extras.DictCursor

        columns = listData[0].keys()

        query = "INSERT INTO public.jptrvl_post({}) VALUES %s".format(','.join(columns))

        # cursor.executemany(insert_query, listData['title'], listData['link'], listData['author'], listData['publish_time'], listData['push_count'], listData['content'])

        # convert projects values to sequence of seqeences
        values = [[value for value in obj.values()] for obj in listData]

        execute_values(cursor, query, values)

        conn.commit()

        count = cursor.rowcount

        print(count, "Record inserted sucessfully into jptrvl")

        cursor.close()

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into table", error)
        conn.rollback()

    finally:
        if cursor:
            cursor.close()
            conn.close()


def close():
    driver.quit()


if __name__ == '__main__':
    visit()
    #     saveJson()
    close()