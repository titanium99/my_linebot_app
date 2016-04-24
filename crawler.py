# coding:utf-8

import requests
import random
import datetime
from bs4 import BeautifulSoup
from tinydb import TinyDB
from apscheduler.schedulers.blocking import BlockingScheduler


# set tinyDB
db = TinyDB("db.json")
db_table = db.table('change_table')
# set apscheduler
sc = BlockingScheduler()


def crawl_site(datequery=None):
    """ PMDAの１ヶ月以内に更新された添付文書情報のスクレイピング用

指定URLのHTMLを取得 """
    if datequery == None:
        url = 'http://www.info.pmda.go.jp/psearch/tenpulist.jsp'
    else:
        url = 'http://www.info.pmda.go.jp/psearch/tenpulist.jsp?DATE={}'.format(datequery)
    htm = requests.get(url).text
    timestamp = datetime.datetime.now().timestamp()
    dest = {'html':htm,'timestamp':timestamp}
    return dest

def scraping_html(src):
    """PMDAの１ヶ月以内に更新された添付文書情報のスクレイピング用
BSで該当tableタグ取得->該当データをdict-> tinyDBに入れる(json保存)
    """
    soup = BeautifulSoup(src['html'])
    table = soup.find('h2', text='掲載分').next_sibling.next_sibling
    tr = table.find_all('tr')
    changelist = []
    for td in tr[1:]:
        tdlist = [i for i in td.find_all('td')]
        update = {}
        update['date'] = soup.find('td',class_='title').text
        update['seihin'] = tdlist[0].text.split()[0]
        update['kigyo'] = tdlist[1].text.split()[0]
        update['status'] = tdlist[2].text.split()[0]
        update['timestamp'] = src['timestamp']
        changelist.append(update)
    db_table.insert_multiple(changelist)


#@sc.scheduled_job('cron', day_of_week='mon-fri', hour='0', minute='26-28')
@sc.scheduled_job('cron', hour='15', minute='12')
def do_scraping():
    src = crawl_site()
    scraping_html(src)

@sc.scheduled_job('cron', hour='10',minute='6-8', id='greet')
def greet():
    now = datetime.datetime.now().strftime('%H:%M:%S')
    with open('test.txt','a') as f:
        f.write('good morning!{}'.format(now))

if __name__ == '__main__':
    sc.start()
