from flask import Flask, render_template, request
import requests
import codecs
import urllib.parse
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def show_top():
    return render_template('index.html')

@app.route('/kekka', methods=['POST'])
def kekka():
    name = request.form['playername']
    search(name)

    return render_template('index.html', name=name,
            old=old, career=career,
            hitrate=hitrate, gamecount=gamecount,
            homerun=homerun, rbi=rbi, ops=ops)


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


app.run(debug=True)