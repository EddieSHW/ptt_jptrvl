#!/usr/bin/env python3
# coding: utf-8

from bs4 import BeautifulSoup as bs
import requests as req
import json
from pprint import pprint
from time import sleep
from random import uniform
import psycopg2
from psycopg2.extras import execute_values

DB_HOST = '127.0.0.1'
DB_PORT = '5432'
DB_NAME = 'jptrvl'
DB_USER = 'postgres'
DB_PASS = 'pttjp_000'

conn_string = f'host={DB_HOST} user={DB_USER} dbname={DB_NAME} password={DB_PASS} port={DB_PORT}'

my_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

listData = []

# url = 'https://www.ptt.cc/bbs/Japan_Travel/index'+str(7296-i)+'.html'

domainName = 'https://www.ptt.cc/bbs/Japan_Travel/index'
pttDomain = 'https://www.ptt.cc'

# total pages = 7296

start_page = 6994
end_page = 6995

sleep_time = uniform(0.1, 0.5)


def get_main_data():
    for page in range(start_page, end_page):
        res = req.get(url=domainName + str(page) + '.html', headers=my_headers)
        # print(res.text)
        soup = bs(res.text, "lxml")
        posts = soup.select('div.r-ent')
        for post in posts:
            if post:
                strTitle = post.select_one('div.title > a').get_text()
                strLink = post.select_one('div.title > a').get('href')
                strAuthor = post.select_one('div.meta > div.author').get_text()
                strPushCount = post.select_one('div.nrec').get_text()

                listData.append({
                    "title": strTitle,
                    "link": strLink,
                    "author": strAuthor,
                    "push_count": strPushCount
                })
            else:
                continue
        # print(listData)


def get_detail_data():
    for index, articleDict in enumerate(listData):
        res = req.get(url=pttDomain + articleDict['link'], headers=my_headers)
        soup = bs(res.text, "lxml")
        metalines = soup.select('div.article-metaline')
        if len(metalines) == 3:
            strTime = metalines[2].select_one('span.article-meta-value').get_text()
            all_text = soup.select_one('div#main-content').get_text()
            pre_text = all_text.split('--')[0]
            texts = pre_text.split('\n')
            contents = texts[4:]
            content = ''.join(contents)
            listData[index]['publish_time'] = strTime
            listData[index]['content'] = content

            sleep(sleep_time)

        else:
            listData[index]['publish_time'] = None
            listData[index]['content'] = None

    pprint(listData)


def save_json():
    with open("pttjptrvl_bs.json", "w", encoding="utf-8") as fp:
        fp.write(json.dumps(listData, ensure_ascii=False, indent=2))


def save_pgdb():
    conn = psycopg2.connect(conn_string)
    print("Connect successfully!")
    try:

        cur = conn.cursor()  # cursor_factory=psycopg2.extras.DictCursor

        columns = listData[0].keys()

        query = "INSERT INTO public.jptrvl_post({}) VALUES %s".format(','.join(columns))

        # convert projects values to sequence of sequences
        values = [[value for value in obj.values()] for obj in listData]

        execute_values(cur, query, values)

        conn.commit()

        count = cur.rowcount

        print(count, "Record inserted successfully into jptrvl")

        cur.close()

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into table", error)
        conn.rollback()

    finally:
        if cur:
            cur.close()
            conn.close()


if __name__ == '__main__':
    get_main_data()
    get_detail_data()
    # save_pgdb()
