import requests
import json
from lxml import etree
import pandas as pd
from datetime import datetime
import time
from collections import defaultdict
import re

# 数据查询页面
# https://yield.chinabond.com.cn/cbweb-mn/indices/multi_index_query?locale=zh_CN


session = requests.Session()


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
}

fp1 = open('tmp.csv', mode='w', encoding='utf8')
fp1.write('code,名称,类型,日期,净值,日增长率,近1周,近1月,近3月,近6月,近1年,近2年,近3年,今年来,成立来,f1,f2,f3,f4,f5,f6,f7,可购买,f9,起购金额,费率,e1,e2,e3\n')

'''
0,0,1,0.00,0,--,041,0,4,---,--,0.00%,--,--
3,1,1,0.06,0,--,041,1,1,10元,0.60%,0.06%,0.06%,1
3,0,1,0.00,0,--,041,1,1,10元,--,0.00%,--,--

0,1,1,0.08,0,--,043,071,0,6,10元,0.80%,0.08%,0.08%,1

3,1,1,0.08,0,,043,045,1,1,10元,0.80%,0.08%,0.08%,1
'''

# 分页查询所有指数
# https://fund.eastmoney.com/trade/zq.html#zwf_,fr_


def _get_total_page():
    
    _url = 'https://fund.eastmoney.com/data/fundtradenewapi.aspx'
    params = {
        'ft': 'zq',
        'sc': '1n',
        'st': 'desc',
        'pi': '1',
        'pn': '100',
        'cp': '',
        'ct': '',
        'cd': '',
        'ms': '',
        'fr': '',
        'plevel':'',
        'fst': '',
        'ftype':'',
        'fr1': '',
        'fl': '0',
        'isab': '',
    }

    text = session.get(_url,params=params, headers=headers).content.decode('utf8')
    all_pages = re.search(r'allPages\s*:\s*(\d+)', text).group(1)
    return all_pages

def _get_page_datas(page):
    
    _url = 'https://fund.eastmoney.com/data/fundtradenewapi.aspx'
    params = {
        'ft': 'zq',
        'sc': '1n',
        'st': 'desc',
        'pi': str(page),
        'pn': '100',
        'cp': '',
        'ct': '',
        'cd': '',
        'ms': '',
        'fr': '',
        'plevel':'',
        'fst': '',
        'ftype':'',
        'fr1': '',
        'fl': '0',
        'isab': '',
    }

    text = session.get(_url,params=params, headers=headers).content.decode('utf8')

    '''
    var rankData = {
        datas: ["020824|汇泉安阳纯债C|债券型|2025-11-20|1.6175|0.00|0.01|0.29|0.29|43.88|49.35|||47.98|101.20|0|0|1|0.00|0||041|0|4|---||0.00%||", "021928|湘财鑫裕纯债A|债券型|2025-11-20|1.4532|0.00|0.01|0.06|0.13|0.01|44.93|||44.69|45.54|3|1|1|0.06|0||041|1|1|10元|0.60%|0.06%|0.06%|1", "007033|平安可转债债券C|债券型|2025-11-20|1.2667|-0.27|-1.45|3.23|0.68|13.22|20.23|15.79|4.77|18.06|26.67|3|0|1|0.00|0||043,045|1|1|10元||0.00%||"],
        allRecords: 5926,
        pageIndex: 1,
        pageNum: 100,
        allPages: 60
    };
    '''

    # all_pages = re.search(r'allPages\s*:\s*(\d+)', text).group(1)
    datas_str = re.search(r'datas\s*:\s*\[(.*?)\]', text, re.S).group(1)
    datas = re.findall(r'"(.*?)"', datas_str)

    global fp1
    for d in datas:
        s1 = d.replace(',','_')
        s = s1.replace('|',',')
        fp1.write(s)
        fp1.write('\n')

    

def main():
    
    total = _get_total_page()
    total = int(total)
    for i in range(1,total+1):

        print(f'download:{total}-{i}')
        _get_page_datas(i)
        time.sleep(1)

    fp1.close()
    # save
    # out = pd.DataFrame(outs)
    # # out.to_excel("国内指数.xlsx", index=False)
    # out.to_csv("中债指数-结果.csv", index=False)


if __name__ == '__main__':
    main()