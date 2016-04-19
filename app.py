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

# create logger
#logger = logging.getLogger('simple_example')
#logger.setLevel(logging.DEBUG)
logging.basicConfig( level=logging.DEBUG)

app = Flask(__name__)
#sc = BlockingScheduler()
inifile = configparser.SafeConfigParser()
inifile.read("./config.ini")
tz_tokyo = pytz.timezone('Asia/tokyo')


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

#@sc.scheduled_job('interval', minutes=1, id='info_job_id')
#def cronjob():
#    to = inifile.get('test','send_to') #test:write lineID
#    now = datetime.now().strftime("%p%I:%M:%S")
#    post_text(to,"Hello info!\nおはようございます.\n現在{}です.".format(now))

@app.route('/')
def index():
    return "<h2>Hello Everyone!</h2>"

@app.route('/callback', methods=['post'])
def hellw():
    #sc.start()
    
    msgs = request.json['result']
    #logger.debug(msgs)
    for msg in msgs:
        logging.debug("%s",msg['content']['from'])
        text = msg['content']['text']
        to = msg['content']['from']
        if text == "何時？":
            now_time(to)
        else:
            post_text(to,text)
    return ""

@app.route('/miya')
def miya():
    return "<h1>こんにちわ!</h1>"


#sc.start()
if __name__ == '__main__':
    app.run(port=8080)
