import requests
import json
from lxml import etree
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

# https://www.csindex.com.cn/#/indices/family/detail?indexCode=000300

def tm_get_13_timestamp():
    dt = datetime.now()
    ts_sec = int(dt.timestamp())
    # 转成 13 位毫秒时间戳
    ts_ms = ts_sec * 1000
    return ts_ms

def s_date_to_13_timestamp(s)->int:
    '''s:20251120'''
    dt = datetime.strptime(s, "%Y%m%d")
    # 转为秒级时间戳
    ts_sec = int(dt.timestamp())
    # 转成 13 位毫秒时间戳
    ts_ms = ts_sec * 1000
    return ts_ms

session = requests.Session()
# session.proxies = {
#     'http': 'http://localhost:7890',
#     'https': 'http://localhost:7890',
# }

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
}


def _get_page_zhishu(page:int):
    
    _url = 'https://www.csindex.com.cn/csindex-home/indexInfo/index-fuzzy-search?searchInput=&pageNum=%d&pageSize=40' % (page)
    text = session.get(_url, headers=headers).content.decode('utf8')

    data = json.loads(text)
    return data


# 分页查询所有指数
# https://www.csindex.com.cn/csindex-home/indexInfo/index-fuzzy-search?searchInput=&pageNum=1&pageSize=10

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
                
            time.sleep(1)
        except Exception as err:
            print(err)
    # save
    out = pd.DataFrame(datas)
    # out.to_excel("国内指数.xlsx", index=False)
    out.to_csv("中证指数.csv", index=False)

    
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
    try:
        data = json.loads(text)
        return data['data']
    except Exception as err:
        print(err)
        return []

def get_start_end_no_craw(indexCode:str, startDate:str, endDate:str):
    '''-->[[1761580800000, val],[]]'''
    _url = 'https://www.csindex.com.cn/csindex-home/perf/indexCsiDsPe'
    params = {
        'indexCode':indexCode,
        'startDate':startDate,
        'endDate':endDate,
        # indexCode=H11025&startDate=20201115&endDate=20251114
    }
    
    text = session.get(_url, params=params, headers=headers).content.decode('utf8')
    try:
        datas = json.loads(text)['data'] # [{}, ]
        # {
        #     "tradeDate": "20230228",
        #     "indexName": "沪深300",
        #     "indexNameEn": "CSI 300",
        #     "peg": 12.14
        # }
        res = []
        for item in datas:
            res.append(
                [s_date_to_13_timestamp(item['tradeDate']), item['peg']]
            )
        return res
    
    except Exception as err:
        print(err)
        return []

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


def calc_year_max_drawdown(data:list):
    '''[(1761580800000, 246.2554), ...]'''

    g_length = len(data)
        
    huiches = []
    
    for i in range(2, g_length):
        _min_data = data[i][0]
        _min = data[i][1]
        _max = 0

        for index,item in enumerate(data[:i]):
            dt2 = item[0]
            value2 = item[1]
            # 向左边找到最大值
            if value2 > _max:
                _max = value2
                _max_date = dt2

        # _max
        # print(f"min: {_min}, _min_date: {datetime.datetime.fromtimestamp(_min_date / 1000).date()}, ")
        
        huiches.append({
            '_min':_min,
            '_min_date':_min_data,
            '_min_date2':datetime.fromtimestamp(_min_data / 1000).date(),
            '_max':_max,
            '_max_date':_max_date,
            '_max_date2':datetime.fromtimestamp(_max_date / 1000).date(),
            'hc':(_max-_min)/_max*100,
        })

    huiches.sort(key=lambda x: x['hc'], reverse=True)
    hc = huiches[0]
    # print(hc)
    return hc

def f_查询某一指数近些年年收益(code:str, start_year:int):
    # r = f_查询某一个指数的基本信息(code)
    # print("近一个月:", r['oneMonth'])
    # print("近三个月:", r['threeMonth'])
    # print("年至今:", r['thisYear'])
    # print("近一年:", r['oneYear'])
    # print("近三年:", r['threeYear'])
    # print("近五年:", r['fiveYear'])
    # time.sleep(1)
    # print("==========")    
    
    rg = datetime.now().year - start_year
     
    print("年份:\t收益\t回撤")
    for i in range(rg):
        startDate = str(start_year+i) + '0101'
        endDate = str(start_year+i) + '1231'
        res = get_start_end_no_craw(code, startDate, endDate)
        if len(res) == 0:
            print(start_year + i,"无数据")
            continue
        start = res[0][1]
        end = res[-1][1]

        # 年化收益
        n1 = (end - start ) / start * 100
        
        # 获取回撤数据
        h1 = calc_year_max_drawdown(res)
        print(start_year + i,"\t", f"{n1:.2f}%", "\t",  f"{h1['hc']:.2f}"+'%',)
        time.sleep(3)


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

# ps:会被限制