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
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@lineapp.route("/")
def hello_world():
    return "hello world!"

@lineapp.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    lineapp.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = search(event.message.text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=msg))


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
    info = soup.find_all("div", class_="NpbTeamTop")[1] # 本名と守備位置
    
    # 本名
    fullname = info.find("h1").contents[0]
    # 守備位置
    position = info.find("span", class_="position").contents[0]
    # 生年月日
    old = profile.find_all("td")[1].contents[0]
    # 経歴
    career = profile.find_all("td")[7].contents[0]

    # 野手か投手か判別
    if position == "投手":
        # 防御率
        era = yjm.find_all("td")[0].contents[0]
        # 登板数
        gamecount = yjm.find_all("td")[1].contents[0]
        # 勝利数
        win = yjm.find_all("td")[8].contents[0]
        # 敗戦数
        lose = yjm.find_all("td")[9].contents[0]
        # ホールド
        hold = yjm.find_all("td")[10].contents[0]
        # セーブ
        save = yjm.find_all("td")[12].contents[0]

        print("防御率:{0} 登板数:{1} 勝利:{2} 敗戦:{3} ホールド:{4} セーブ:{5}"
                .format(era,gamecount,win,lose,hold,save))
        ans = fullname+"("+position+")"+"\n"+old+"\n"+career+"\n"
                +"防御率: "+era+"\n"+"登板数: "+gamecount+"\n"
                +"勝利: "+win+"\n"+"敗戦: "+lose+"\n"+"ホールド: "+hold+"\n"
                +"セーブ: "+save

    else:
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

        ans = fullname+"("+position+")"+"\n"+old+"\n"+career+"\n"
                +"打率: "+hitrate+"\n"+"試合数: "+gamecount+"\n"
                +"本塁打: "+homerun+"\n"+"打点: "+rbi+"\n"+"OPS: "+ops

    return ans


if __name__ == '__main__':
    lineapp.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


