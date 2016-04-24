# coding:utf-8

from flask import Flask
from flask import request

import requests
import json
import re
import logging
#from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import pytz
import configparser
from tinydb import TinyDB, Query
from bs4 import BeautifulSoup

# create logger
#logger = logging.getLogger('simple_example')
#logger.setLevel(logging.DEBUG)
logging.basicConfig( level=logging.DEBUG)

app = Flask(__name__)
# read initfile
inifile = configparser.SafeConfigParser()
inifile.read("./config.ini")
# setting timezone
tz_tokyo = pytz.timezone('Asia/Tokyo')
# setting tinyDB
db = TinyDB('db.json')
db_table = db.table('change_table')

# set line api
LINEBOT_API_EVENT ='https://trialbot-api.line.me/v1/events'
LINE_HEADERS = {
        'Content-type': 'application/json; charset=UTF-8',
        'X-Line-ChannelID': inifile.get('LINE_HEADERS','Channel_ID'),
        'X-Line-ChannelSecret': inifile.get('LINE_HEADERS','Channel_Secret'),
        'X-Line-Trusted-User-With-ACL': inifile.get('LINE_HEADERS','Channel_MID')
    }

def post_event( to, content):
    msg = {
        'to': [to],
        'toChannel': 1383378250, # Fixed  value
        'eventType': "138311608800106203", # Fixed value
        'content': content
    }
    r = requests.post(LINEBOT_API_EVENT, headers=LINE_HEADERS, data=json.dumps(msg))

def post_text( to, text ):
    content = {
        'contentType':1,
        'toType':1,
        'text':text,
    }
    post_event(to, content)

def now_time(to):
    timeformat = "%p%I:%M:%S"
    utcnow = datetime.now().strftime(timeformat)
    tknow = datetime.now(tz_tokyo).strftime(timeformat)
    post_text(to,"こんにちわ！.\n現在{}です.".format(tknow))

def search_db(querystr,queryday=datetime.now().strftime("%m月%d日")):
    qr = Query()
    qr = db_table.search(qr.date.search(queryday) & 
            qr.kigyo.search(querystr))
    res = {i['seihin'] for i in qr}
    return res

def ydn_post_text(msg):
    jlp_url = 'http://jlp.yahooapis.jp/MAService/V1/parse'
    params = {'appid': inifile.get('yahoo_api','appid'),
            'sentence': msg,
            'results': 'ma',
            'filter': '9'}
    resxml = requests.get(jlp_url,params=params)
    soup = BeautifulSoup(resxml.text)
    rslt = [i for i in soup.ma_result.word_list]
    return [j.surface.string for j in rslt]


@app.route('/')
def index():
    return "<h2>Hello Everyone!</h2>"

@app.route('/callback', methods=['post'])
def hellw():
    msgs = request.json['result']
    #logger.debug(msgs)
    for msg in msgs:
        logging.debug("%s",msg['content']['from'])
        text = msg['content']['text']
        to = msg['content']['from']
        if text == "何時？":
            now_time(to)
        elif re.search(u"更新情報(：|:)",text):
            morph = ydn_post_text(msgs)
            kigyo = morph[morph.index("情報") + 1]
            kousin = search_db(kigyo)
            if len(kousin) == 0:
                post_text(to, "本日の更新はないです。")
            else:
                res = "本日の更新は下記になります。\n{}".format("\n".join(kousin))
                post_text(to,res)
        else:
            post_text(to,text)
    return ""

@app.route('/miya')
def miya():
    return "<h1>こんにちわ!</h1>"


if __name__ == '__main__':
    app.run(port=8080)
