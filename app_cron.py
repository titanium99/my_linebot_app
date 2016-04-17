# coding:utf-8

from flask import Flask
from flask import request

import requests
import json
import re
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

# create logger
#logger = logging.getLogger('simple_example')
#logger.setLevel(logging.DEBUG)
logging.basicConfig( level=logging.DEBUG)

app = Flask(__name__)
sc = BlockingScheduler()

LINEBOT_API_EVENT ='https://trialbot-api.line.me/v1/events'
LINE_HEADERS = {
        'Content-type': 'application/json; charset=UTF-8',
        'X-Line-ChannelID':'1462403791',
        'X-Line-ChannelSecret':'46ce7e5af1895e03405f36f974a65782',
        'X-Line-Trusted-User-With-ACL':'uf1e01ab31a1e14759fb10edbacbf85d2'
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

@sc.scheduled_job('interval', minutes=1, id='info_job_id')
def cronjob():
    to ='u0caebf34a26807a73c08fed9201735d5' #lineID
    now = datetime.now().strftime("%p%I:%M:%S")
    post_text(to,"Hello info!\nおはようございます.\n現在{}です.".format(now))

@app.route('/')
def index():
    return "<h2>This site is moved.</h2>"

@app.route('/callback', methods=['post'])
def hellw():
    #sc.start()
    
    msgs = request.json['result']
    #logger.debug(msgs)
    for msg in msgs:
        logging.debug("%s",msg['content']['from'])
        text = msg['content']['text']
        post_text(msg['content']['from'],text)
    return ""

@app.route('/miya')
def miya():
    return "<h1>こんにちわ!</h1>"


sc.start()
if __name__ == '__main__':
    #context =('/etc/nginx/ssl/bot.mshiro.co/ssl/ssl-bundle.crt','/etc/nginx/ssl/bot.mshiro.co/bot_mshiro_co.key')
    #app.run(host='127.0.0.1', port=8080)
    
    app.run(port=8080)
