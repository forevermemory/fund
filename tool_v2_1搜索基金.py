import requests
import json
import re
from lxml import etree
from bs4 import BeautifulSoup
import pandas as pd
import time

session = requests.Session()



def do_search(key:str):
    now = str(int(time.time() * 1000))
    params = {
        'callback': 'jQuery18308932037864680957_1762998769877',
        'm': '0',
        'key': key,
        '_': now,
    }
    _url = 'https://fundsuggest.eastmoney.com/FundSearch/api/FundSearchPageAPI.ashx'

    
    print("first search start:")

    r = session.get(_url, params=params)
    r.encoding = "utf-8" 
    m = re.search(r'\((.*)\)', r.text, re.S)
    if m == None:
        print("未知的数据类型")
        return

    json_data = json.loads(m.group(1))
    if json_data['ErrCode'] != 0:
        print("ErrCode", json_data['ErrCode'])
        return
    
    data = json_data['Datas'] # {}
    items = data['FundList']
    page_size = len(data['FundList'])
    page_total = data['FundListTotalCount']
    
    print("first search:", page_size, page_total)
    if page_total > page_size:
        # 请求更多
        params = {
            'callback': 'jQuery18308932037864680957_1762998769877',
            'm': '1',
            'key': key,
            '_': now,
            'pageindex': '0',
            'pagesize': str(page_total),
        }
        
        print("next search:", page_size, page_total)
        r = session.get(_url, params=params)
        r.encoding = "utf-8" 
        m = re.search(r'\((.*)\)', r.text, re.S)
        if m is None:
            print("未知的数据类型")
            return

        json_data = json.loads(m.group(1))
        if json_data['ErrCode'] != 0:
            print("ErrCode", json_data['ErrCode'])
            return
        
        items = json_data['Datas']
        print('=========',len(items))

    print("write data")
    out = pd.DataFrame(items)
    out.to_excel("out.xlsx", index=False)
    out.to_csv("out.csv", index=False)

def main():
    do_search("沪深300")


if __name__ == '__main__':
    main()
    