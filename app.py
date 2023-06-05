#!/usr/bin/env python3
# coding: utf-8

from flask import Flask, render_template, request
from wordcloud import WordCloud
import pandas as pd
import plotly.graph_objects as go
import jieba

app = Flask(__name__)


@app.route('/')
def index():
    # 讀取CSV檔案
    df = pd.read_csv('jptrvl_post_time.csv')
    df_ex = pd.read_csv('exchange_rates.csv')
    # 獲取所有日期
    dates = sorted(df['Date'].unique())
    # 轉換匯率表格日期
    df_ex['Date'] = pd.to_datetime(df_ex['Date'])
    # 設定圖表佈局
    layout = go.Layout(
        title='日圓匯率',
        xaxis=dict(title='日期'),
        yaxis=dict(title='匯率')
    )

    # 繪製折線圖
    fig = go.Figure(data=go.Scatter(x=df_ex['Date'], y=df_ex['Buy'], name='買入', mode='lines'),
                    layout=layout)
    fig.add_trace(go.Scatter(x=df_ex['Date'], y=df_ex['Sell'], name='賣出', mode='lines'))

    # 生成折線圖的HTML
    line_chart = fig.to_html(full_html=False, default_height=600)

    return render_template('index.html', dates=dates, wordcloud_img=None, line_chart=line_chart)


@app.route('/wordcloud', methods=['GET'])
def generate_wordcloud():
    # 讀取CSV檔案
    df = pd.read_csv('jptrvl_post_time.csv')
    # 獲取選擇的日期
    selected_date = request.args.get('date')
    # 選擇相同日期的文章內容
    df = df[df['Date'].str.contains(selected_date)]
    # 合併文章內容
    text = ' '.join(df['content'])
    # 分詞處理
    text = ' '.join(jieba.cut(text))

    # 生成文字雲
    wc = WordCloud(font_path='/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc', background_color="white",
                   width=800, height=600, max_words=500, min_font_size=4, collocations=False).generate(text)

    wc_img_path = 'static/image/wordcloud.png'
    wc.to_file(wc_img_path)

    return render_template('index.html', dates=sorted(df['Date'].unique()), wordcloud_img=wc_img_path)


if __name__ == '__main__':
    app.run(debug=True)
