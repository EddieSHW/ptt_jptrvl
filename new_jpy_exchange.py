import requests as req
from bs4 import BeautifulSoup as bs
import csv
from time import sleep

url = "https://historical.findrate.tw/his.php?c=JPY&page="
my_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

start_page = 1
end_page = 12

pageData = []

for page in range(start_page, end_page + 1):
    res = req.get(url + str(page), headers=my_headers)
    soup = bs(res.content, "lxml")
    table = soup.select_one("table")
    rows = table.find_all("tr")
    pageData.append(rows)
    sleep(1)

with open("exchange_rates.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Date", "Buy", "Sell"])

    # 迭代每一列，跳過表頭
    for obj in pageData:
        for row in obj[1:]:
            # 取得列中的每一格資料
            cells = row.find_all("td")
            date = cells[0].text.strip()
            buy_rate = cells[1].text.strip()
            sell_rate = cells[2].text.strip()

            # 將資料寫入CSV檔案
            writer.writerow([date, buy_rate, sell_rate])

print("爬取完成！資料已儲存為exchange_rates.csv檔案。")
