#!/usr/bin/env python3
# coding: utf-8

from bs4 import BeautifulSoup as bs
import requests as req
import json
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

# total pages = 7572
# 2020 start = 6994
# 2022 start = 7219
# 7186 enoshima error

start_page = 7219
end_page = 7572

sleep_time = uniform(1, 1.5)


def get_main_data():
    for page in range(start_page, end_page + 1):
        res = req.get(url=domainName + str(page) + '.html', headers=my_headers)
        # print(res.text)
        soup = bs(res.text, "lxml")
        posts = soup.select('div.r-ent')
        for post in posts:
            if post is not None:
                if post.select_one('div.title > a') is not None:
                    str_title = post.select_one('div.title > a').get_text()
                    str_link = post.select_one('div.title > a').get('href')
                    str_author = post.select_one('div.meta > div.author').get_text()
                    str_push_count = post.select_one('div.nrec').get_text()

                    listData.append({
                        "title": str_title,
                        "link": str_link,
                        "author": str_author,
                        "push_count": str_push_count
                    })
                else:
                    continue
            else:
                continue

        # print(listData)


def get_detail_data():
    for index, articleDict in enumerate(listData):
        res = req.get(url=pttDomain + articleDict['link'], headers=my_headers)
        soup = bs(res.text, "lxml")
        metalines = soup.select('div.article-metaline')
        if len(metalines) == 3:
            str_time = metalines[2].select_one('span.article-meta-value').get_text()
            all_text = soup.select_one('div#main-content').get_text()
            pre_text = all_text.split('--')[0]
            texts = pre_text.split('\n')
            contents = texts[1:]
            content = ''.join(contents)
            listData[index]['publish_time'] = str_time
            listData[index]['content'] = content

            sleep(sleep_time)

        else:
            listData[index]['publish_time'] = None
            listData[index]['content'] = None

    # pprint(listData)
        print(f'{index + 1} posts have been scrapped!')


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

        # for row in values:
        #     try:
        #         execute_values(cur, query, [row])
        #     except (Exception, psycopg2.Error) as error:
        #         print("Failed to insert record into table:", error)
        #         conn.rollback()
        #         continue

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
    save_pgdb()
