from flask import Flask, request, abort
import os
import requests
import codecs
import urllib.parse
from bs4 import BeautifulSoup
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

lineapp = Flask(__name__)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route('/callback', methods=['POST'])
def callback():
    # X-Line-Signatureヘッダーの取得
    signature = request.headers['X-Line-Signature']

    # リクエストの取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    search(event.message.text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=old))

def search(name):
    s = name
    sq = urllib.parse.quote(s)
    linkto = "https://search.yahoo.co.jp/search?p={}&fr=spo_npb&ei=utf-8&vs=baseball.yahoo.co.jp".format(sq)

    html = requests.get(linkto).content
    soup = BeautifulSoup(html, "html.parser")
    # 選手データのページ
    dataurl = [a.get("href") for a in soup.find_all("a")][3]


    dataurl = requests.get(dataurl).content
    soup = BeautifulSoup(dataurl, "html.parser")
    yjm = soup.find_all("tr", class_="yjM")[0]
    yjmops = soup.find_all("tr", class_="yjM")[1]
    profile = soup.find_all("div", class_="yjS")[0]

    
    global old,career,hitrate,gamecount,homerun,rbi,ops
    # 生年月日
    old = profile.find_all("td")[1].contents[0]
    # 経歴
    career = profile.find_all("td")[7].contents[0]
    # 打率
    hitrate = yjm.find_all("td")[0].contents[0]
    # 試合数
    gamecount = yjm.find_all("td")[1].contents[0]
    # 本塁打数
    homerun = yjm.find_all("td")[7].contents[0]
    # 打点数
    rbi = yjm.find_all("td")[9].contents[0]
    # OPS
    ops = yjmops.find_all("td")[9].contents[0]



if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    lineapp.run(host="0.0.0.0", port=port)


