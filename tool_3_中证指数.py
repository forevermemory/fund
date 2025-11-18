import requests
import json
from lxml import etree
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

# https://www.csindex.com.cn/#/indices/family/detail?indexCode=000300


session = requests.Session()
# session.proxies = {
#     'http': 'http://localhost:7890',
#     'https': 'http://localhost:7890',
# }

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
}



# 分页查询所有指数
# https://www.csindex.com.cn/csindex-home/indexInfo/index-fuzzy-search?searchInput=&pageNum=1&pageSize=10


def _get_page_zhishu(page:int):
    
    _url = 'https://www.csindex.com.cn/csindex-home/indexInfo/index-fuzzy-search?searchInput=&pageNum=%d&pageSize=10' % (page)
    text = session.get(_url, headers=headers).content.decode('utf8')

    data = json.loads(text)
    return data

def f_分页查询所有指数():
    
    data = _get_page_zhishu(1)
    total_page = int(data['size'])
    
    datas = []
    
    print('total_page:',total_page)
    for i in range(total_page):
        cur_page = i+1
        print("下载:",total_page, cur_page)
        
        try:
            data = _get_page_zhishu(cur_page)
            for a in data['data']:
                a['查看地址'] = 'https://www.csindex.com.cn/#/indices/family/detail?indexCode='+a['indexCode']
                datas.append(a)
            
        except Exception as err:
            print(err)
    # save
    out = pd.DataFrame(datas)
    out.to_excel("国内指数.xlsx", index=False)
    # out.to_csv("国内指数.csv", index=False)
    pass
    
# 查询近几年数据
# https://www.csindex.com.cn/csindex-home/perf/get-index-yield-item/H11025


# 查询年化
# https://www.csindex.com.cn/csindex-home/perf/get-index-yield-item-nianHua/000016


def get_start_end(indexCode:str, startDate:str, endDate:str):
    _url = 'https://www.csindex.com.cn/csindex-home/perf/index-perf'
    params = {
        'indexCode':indexCode,
        'startDate':startDate,
        'endDate':endDate,
        # indexCode=H11025&startDate=20201115&endDate=20251114
    }
    
    text = session.get(_url, params=params, headers=headers).content.decode('utf8')
    data = json.loads(text)
    return data['data']


def f_查询某一个指数的基本信息(code:str):
    # https://www.csindex.com.cn/csindex-home/perf/get-index-yield-item/000300
    _url = 'https://www.csindex.com.cn/csindex-home/perf/get-index-yield-item/'+code
    
    text = session.get(_url, headers=headers).content.decode('utf8')
    data = json.loads(text)
    # {
    #     "code": "200",
    #     "msg": "Success",
    #     "data": {
    #         "indexCode": "000300",
    #         "indexNameCn": "沪深300",
    #         "indexNameEn": "CSI 300",
    #         "endDate": "2025-11-14",
    #         "oneMonth": "1.96",
    #         "threeMonth": "10.90",
    #         "thisYear": "17.62",
    #         "oneYear": "14.57",
    #         "threeYear": "6.85",
    #         "fiveYear": "-0.96",
    #         "oneYearNianHua": null,
    #         "threeYearNianHua": null,
    #         "fiveYearNianHua": null
    #     },
    #     "success": true
    # }
    return data['data']

    pass

def f_查询某一指数近些年年收益(code:str, start_year:int):
    r = f_查询某一个指数的基本信息(code)
    print("近一个月:", r['oneMonth'])
    print("近三个月:", r['threeMonth'])
    print("年至今:", r['thisYear'])
    print("近一年:", r['oneYear'])
    print("近三年:", r['threeYear'])
    print("近五年:", r['fiveYear'])
    time.sleep(1)
    print("==========")    
    
    rg = datetime.now().year - start_year
     
    print("年份:\t收益\t回撤")
    for i in range(rg):
        startDate = str(start_year+i) + '0101'
        endDate = str(start_year+i) + '1231'
        res = get_start_end(code, startDate, endDate)
        start = res[0]['close']
        end = res[-1]['close']
        
        # 获取回撤数据
        _max = 0
        _min = res[0]['close']
        for d in res:
            v = d['close']
            if v > _max:
                _max = v
            if v < _min:
                _min = v
        
        _huiche = (_max-_min) / _max

        num = (end - start) / start * 100
        print(start_year + i,"\t", f"{num:.2f}"+'%', "\t",  f"{_huiche*100:.2f}"+'%',)
        time.sleep(1)


    # {
    #     "tradeDate": "20201115",
    #     "indexCode": "H11025",
    #     "indexNameCnAll": "中证货币基金指数",
    #     "indexNameCn": "货币基金",
    #     "indexNameEnAll": "CSI Money Fund Index",
    #     "indexNameEn": "Money Fund",
    #     "open": null,
    #     "high": null,
    #     "low": null,
    #     "close": 1578.28,
    #     "change": 0.28,
    #     "changePct": 0.02,
    #     "tradingVol": null,
    #     "tradingValue": null,
    #     "consNumber": 681,
    #     "peg": null
    # }
    
    
    year = datetime.now().strftime("%Y")
    today = datetime.now().strftime("%Y%m%d")
    res = get_start_end(code, year+'0101', today)
    start = res[0]['close']
    end = res[-1]['close']

    num = (end - start) / start * 100
    print('至今'+today,"\t", f"{num:.2f}"+'%'"\t","0%")
    

def main():
    # f_分页查询所有指数()


    f_查询某一指数近些年年收益('000300', 2000)
    pass

    
if __name__ == '__main__':
    main()