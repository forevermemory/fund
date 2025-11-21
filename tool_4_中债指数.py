import requests
import json
from lxml import etree
import pandas as pd
from datetime import datetime
import time
from collections import defaultdict


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

def calc_year_annualized(data:list):
    '''计算年化收益: [(1761580800000, 246.2554), ...]'''
    _start = data[0][1]
    _end = data[-1][1]
    return _end - _start

def year_data_group_by_year(data:list)->dict:
    '''data: [[20251120, 11.1],...]'''
    groups = defaultdict(list)

    for ts_ms, value in data:
        # 毫秒时间戳 -> datetime
        dt = datetime.fromtimestamp(ts_ms / 1000)
        # groups[year].append((dt, value))
        
        ### 
        # ps:有些有很多年的数据,不需要超过8年的
        # if dt.year < cur_year - 8:
        #     continue
        
        groups[dt.year].append((ts_ms, value))
    return groups

# 数据查询页面
# https://yield.chinabond.com.cn/cbweb-mn/indices/multi_index_query?locale=zh_CN


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


def _get_page_zhishu(z1:str, z2:str):
    
    _url = 'https://yield.chinabond.com.cn/cbweb-mn/indices/multiIndexQuery'
    params = {
        'zs1': z1,
        'zslx1': 'CFZS',
        'qxlx1': '00',
        'zs2': z2,
        'zslx2': 'CFZS',
        'qxlx2': '00',
        'locale': 'zh_CN',
    }

    text = session.post(_url,params=params, headers=headers).content.decode('utf8')

    # fp = open('res.json', encoding='utf8', mode='w')
    # fp.write(text)
    # fp.close()

    data = json.loads(text)
    return data

def get_z1_z2(z1:str,z2:str) -> dict:
    datas = _get_page_zhishu(z1, z2)
    # datas: {"dataType2":["00"],"dataType1":["00"],"CFZS_8a8b2ca05242607601524498b2133d9a_00":{} }

    _k1 = f'CFZS_{z1}_00'
    zs1 = datas[_k1] # {'timestamp': val, ... }
    _k2 = f'CFZS_{z2}_00'
    zs2 = datas[_k2]

    print("编码\t年份\t收益\t回撤\t")
    data = []
    for k in zs1:
        # dt = datetime.fromtimestamp(int(k) / 1000)
        data.append([int(k), float(zs1[k])])

    groups = year_data_group_by_year(data)

    result = {}
    rz1 = []
    for year, items in groups.items():
        # items: [(1761580800000, 246.2554), ...]

        n1 = calc_year_annualized(items)
        hc = calc_year_max_drawdown(items)
        print(z1,year, n1, hc['hc'])
        rz1.append({
            'year':year,
            'n1':n1,
            'hc':hc['hc'],
        })
    result[z1] = rz1

    data = []
    for k in zs2:
        # dt = datetime.fromtimestamp(int(k) / 1000)
        data.append([int(k), float(zs2[k])])

    groups = year_data_group_by_year(data)
    rz2 = []

    for year, items in groups.items():
        # items: [(1761580800000, 246.2554), ...]

        n1 = calc_year_annualized(items)
        hc = calc_year_max_drawdown(items)
        print(z2, year, n1, hc['hc'])
        rz2.append({
            'year':year,
            'n1':n1,
            'hc':hc['hc'],
        })
    result[z2] = rz2

    return result

def main():
    # f_分页查询所有指数()
    # get_z1_z2('2c9081e50e8767dc010e879acb220021', '8a8b2ca05242607601524498b2133d9a')
    # 中债-国债总指数 2c9081e50e8767dc010e879acb220021
    # 中债-7-10年国开行债券指数 8a8b2ca05242607601524498b2133d9a

    z1 = '2c90818811d3f4fa01123837e6b30d4a'
    z1_desc = '企业债总指数'
    z2 = '8a8b2ca050d9e35d0150da6758462c78'
    z2_desc = '公司债总指数'
    result2 = get_z1_z2(z1, z2)
    # {z1:[{}, ...]}

    outs = []
    for item in result2[z1]:
        outs.append({
            '编码':z1_desc,
            '年份':item['year'],
            '收益':item['n1'],
            '回撤':item['hc'],
        })
    for item in result2[z2]:
        outs.append({
            '编码':z2_desc,
            '年份':item['year'],
            '收益':item['n1'],
            '回撤':item['hc'],
        })

    # save
    out = pd.DataFrame(outs)
    # out.to_excel("国内指数.xlsx", index=False)
    out.to_csv("中债指数-结果.csv", index=False)


if __name__ == '__main__':
    main()