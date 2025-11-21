import requests
import json
import re
from lxml import etree
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from datetime import datetime,date
from collections import defaultdict

from PyQt5 import QtWidgets
from PyQt5.Qt import *

session = requests.Session()

from tools.mylog import _my_print as mylog__mxxxxx


def s_date_calc_since_totay(s)->int:
    '''s:2009-07-21'''
    target = datetime.strptime(s, "%Y-%m-%d").date()
    today = date.today()

    delta_days = (today - target).days
    return delta_days

def s_date_2_to_13_timestamp(s)->int:
    '''s:2009-07-21'''
    dt = datetime.strptime(s, "%Y-%m-%d")
    # 转为秒级时间戳
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

def tm_get_13_timestamp() -> int:
    dt = datetime.now()
    ts_sec = int(dt.timestamp())
    ts_ms = ts_sec * 1000
    return ts_ms


def calc_year_max_drawdown(data:list) ->dict:
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

def calc_year_annualized(data:list)->float:
    '''计算年化收益: [(1761580800000, 246.2554), ...]'''
    _start = data[0][1]
    _end = data[-1][1]
    return _end - _start

def _my_print(s):
    mylog__mxxxxx(s)

def parse_jsonp_response(data: str):
    m = re.search(r'\((.*)\)', data, re.S)
    if m == None:
        return None

    json_data = json.loads(m.group(1))
    return json_data


def check_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def check_file_is_exist(fp: str) -> bool:
    if os.path.exists(fp):
        return True
    return False


def get_year_month_day() -> str:
    now = datetime.now()
    return f"{now.year}-{now.month}-{now.day}"


def tt_do_search_zhishu(key: str, out_dir: str):
    now = str(int(time.time() * 1000))
    params = {
        'callback': 'jQuery18308932037864680957_1762998769877',
        'm': '0',
        'key': key,
        '_': now,
    }
    _url = 'https://fundsuggest.eastmoney.com/FundSearch/api/FundSearchPageAPI.ashx'

    _my_print("first search start:")

    r = session.get(_url, params=params)
    r.encoding = "utf-8"
    m = re.search(r'\((.*)\)', r.text, re.S)
    if m is None:
        _my_print("未知的数据类型")
        return

    json_data = json.loads(m.group(1))
    if json_data['ErrCode'] != 0:
        _my_print("ErrCode")
        return

    data = json_data['Datas']  # {}
    items = data['FundList']
    page_size = len(data['FundList'])
    page_total = data['FundListTotalCount']

    s1 = "first search: %d - %d" % (page_size, page_total)
    _my_print(s1)
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
        s1 = "next search: %d - %d" % (page_size, page_total)
        _my_print(s1)
        r = session.get(_url, params=params)
        r.encoding = "utf-8"
        m = re.search(r'\((.*)\)', r.text, re.S)
        if m is None:
            _my_print("未知的数据类型")
            return

        json_data = json.loads(m.group(1))
        if json_data['ErrCode'] != 0:
            _my_print("ErrCode")
            return

        items = json_data['Datas']
        s1 = '累计数据:%d' % (len(items))
        _my_print(s1)

    _my_print("write data")
    out = pd.DataFrame(items)

    out.to_excel(f"{out_dir}/{key}.xlsx", index=False)
    out.to_csv(f"{out_dir}/{key}.csv", index=False)


def _tt_do_search_fund_item(code: str)->dict:
    now = str(int(time.time() * 1000))

    _url = 'https://fund.eastmoney.com/%s.html' % (code)

    r = session.get(_url)
    # 可能是后端，然后重定向

    text = r.content.decode('utf8')

    # fp = open('b.html', encoding='utf8')
    # text = fp.read()
    # fp.close()

    # html = etree.HTML(text)

    soup = BeautifulSoup(text, "lxml")

    # name = soup.select('#body > div:nth-child(11) > div > div > div.fundDetail-header > div.fundDetail-tit > div')[0].text

    # part1
    container_base = '#body > div:nth-child(11) > div > div > div.fundDetail-main'
    part1 = soup.select(container_base + ' > div.fundInfoItem > div.dataOfFund')

    # print(len(part1))
    if len(part1) == 0:
        container_base = '#body > div:nth-child(12) > div > div > div.fundDetail-main'
        part1 = soup.select(container_base + ' > div.fundInfoItem > div.dataOfFund')


    #
    cur_year = datetime.now().year
    y0_desc = str(cur_year)
    y1_desc = str(cur_year-1)
    y2_desc = str(cur_year-2)
    y3_desc = str(cur_year-3)
    y4_desc = str(cur_year-4)
    y5_desc = str(cur_year-5)
    y6_desc = str(cur_year-6)
    y7_desc = str(cur_year-7)
    y8_desc = str(cur_year-8)

    if len(part1) == 0:
        # 重定向到前端基金
        data = {
            '代码': code,
            '名称': '后端',
            '累计净值': '',
            '规模': '',
            '基金经理': '',
            '成立日': '',
            '管理人': '',
            '跟踪标的': '',
            '年化跟踪误差': '',
            '交易状态': '',
            '购买手续费': '',
            '近1周': '',
            '近1月': '',
            '近3月': '',
            '近6月': '',
            '今年来': '',
            '近1年': '',
            '近2年': '',
            '近3年': '',
            '成立来': '',
             y1_desc: '',
            y2_desc: '',
            y3_desc: '',
            y4_desc: '',
            y5_desc: '',
            y6_desc: '',
            y7_desc: '',
            y8_desc: '',
        }
        return data

    dls = part1[0].find_all('dl')
    # print(len(dls))

    dl_index = len(dls) - 1
    累计净值 = ''
    累计净值 = dls[dl_index].find_all('dd')[0].find_all('span')[0].text
    成立来 = dls[dl_index].find_all('dd')[2].find_all('span')[1].text

    # print( 累计净值, 成立来)

    part2 = soup.select(container_base + " > div.fundInfoItem > div.infoOfFund > table")[0]
    trs = part2.find_all('tr')
    规模_r = trs[0].find_all('td')[1].text.replace('规模：', '')
    规模 = re.sub(r'[\(（亿元（][^)]*[\)）]', '', 规模_r)

    基金经理 = trs[0].find_all('td')[2].find('a').text

    成立日 = trs[1].find_all('td')[0].text.replace('成 立 日', '').replace('：', '')
    管理人 = trs[1].find_all('td')[1].find('a').text

    # 这里可能数据缺失
    跟踪标的 = ''
    年化跟踪误差 = ''
    try:
        txt1 = trs[2].find_all('td')[0].text
        跟踪标的 = txt1.split('|')[0].replace('跟踪标的：', '').strip()
        年化跟踪误差 = txt1.split('|')[1].replace('年化跟踪误差：', '')
    except Exception as err:
        # print("==================跟踪缺失,", code)
        pass

    # print(规模, 基金经理, 成立日, 管理人, 跟踪标的, 年化跟踪误差)

    # 交易方式
    交易状态 = ''
    购买手续费 = ''
    pf1 = soup.select(container_base + " > div > div.buyWayWrap > div.buyWayStatic")
    try:
        交易状态 = pf1[0].find_all('div')[0].find_all('span')[1].text
        购买手续费 = pf1[0].find_all('div')[4].find_all('span')[1].text.strip()
    except Exception as err:
        pass

    # print(交易状态, 购买手续费)

    part3 = soup.select("#increaseAmount_stage > table > tr")

    #
    cur = part3[1].find_all('td')
    近1周 = cur[1].find('div').text
    近1月 = cur[2].find('div').text
    近3月 = cur[3].find('div').text
    近6月 = cur[4].find('div').text
    今年来 = cur[5].find('div').text
    近1年 = cur[6].find('div').text
    近2年 = cur[7].find('div').text
    近3年 = cur[8].find('div').text
    # print(近1周, 近1月, 近3月, 近6月, 今年来, 近1年, 近2年, 近3年)

    p4 = soup.select('#IncreaseAmount > div.bd > ul > li')
    niandu_desc = p4[2].find('table').find_all('tr')[0].find_all('th')

    # y1_desc = niandu_desc[1].find('div').text
    # y2_desc = niandu_desc[2].find('div').text
    # y3_desc = niandu_desc[3].find('div').text
    # y4_desc = niandu_desc[4].find('div').text
    # y5_desc = niandu_desc[5].find('div').text
    # y6_desc = niandu_desc[6].find('div').text
    # y7_desc = niandu_desc[7].find('div').text
    # y8_desc = niandu_desc[8].find('div').text

    # print(y1_desc, y2_desc, y3_desc, y4_desc, y5_desc, y6_desc, y7_desc, y8_desc)

    niandu = p4[2].find('table').find_all('tr')[1].find_all('td')
    y1 = niandu[1].find('div').text
    y2 = niandu[2].find('div').text
    y3 = niandu[3].find('div').text
    y4 = niandu[4].find('div').text
    y5 = niandu[5].find('div').text
    y6 = niandu[6].find('div').text
    y7 = niandu[7].find('div').text
    y8 = niandu[8].find('div').text

    # print(y1, y2, y3, y4, y5, y6, y7, y8)

    data = {
        '代码': code,
        '名称': '',
        '累计净值': 累计净值,
        '规模': 规模,
        '基金经理': 基金经理,
        '成立日': 成立日,
        '管理人': 管理人,
        '跟踪标的': 跟踪标的,
        '年化跟踪误差': 年化跟踪误差,
        '交易状态': 交易状态,
        '购买手续费': 购买手续费,
        '近1周': 近1周,
        '近1月': 近1月,
        '近3月': 近3月,
        '近6月': 近6月,
        '今年来': 今年来,
        '近1年': 近1年,
        '近2年': 近2年,
        '近3年': 近3年,
        '成立来': 成立来,
        y1_desc: y1,
        y2_desc: y2,
        y3_desc: y3,
        y4_desc: y4,
        y5_desc: y5,
        y6_desc: y6,
        y7_desc: y7,
        y8_desc: y8,
    }

    # print(data)
    return data


def tt_do_search_zhishu_detail(_key: str,  out_dir: str):
    '''搜素指数基金详情'''
    fname = f"{out_dir}/{_key}.xlsx"

    df = pd.read_excel(fname, dtype=str)

    datas = []
    num_rows = len(df)

    for index, row in df.iterrows():
        code = row["CODE"]
        name = row["NAME"]

        if index > 2:
            break

        try:
            r1 = _tt_do_search_fund_item(code)
            r1['名称'] = name
            datas.append(r1)

            s1 = f"处理完成:{num_rows}-{index+1}, {name}"
            
            _my_print(s1)
            print(s1)
        except Exception as err:
            s1 = f"处理失败-----:{code}, {name}"
            _my_print(s1)

    out = pd.DataFrame(datas)
    out.to_excel(f"{out_dir}/{_key}-详情.xlsx", index=False)
    out.to_csv(f"{out_dir}/{_key}-详情.csv", index=False)






def _tt_do_get_max_drawdown(code:str) -> dict:
    '''获取某一只的年度最大回撤'''
    now = datetime.now()
    now_str = f'{now.year}{now.month}{now.day}{now.hour}{now.minute}{now.second}'
    _url = 'https://fund.eastmoney.com/pingzhongdata/%s.js?v=%s' % (code, now_str)
    
    # print(_url)
    r = session.get(_url)
    js_source = r.content.decode('utf8')
    # js_source = js_source
    
    pattern = r"Data_ACWorthTrend\s*=\s*(\[\s*[\s\S]*?\s*\])\s*;"
    match = re.search(pattern, js_source, re.S)
    if not match:
        return None
    array_str = match.group(1)
    
    cur_year = datetime.now().year # 2025
    
    data = json.loads(array_str)
    data:list
    groups = defaultdict(list)

    for ts_ms, value in data:
        # 毫秒时间戳 -> datetime
        dt = datetime.fromtimestamp(ts_ms / 1000)
        # groups[year].append((dt, value))
        
        ### 
        # ps:有些有很多年的数据,不需要超过8年的
        if dt.year < cur_year - 8:
            continue
        
        groups[dt.year].append((ts_ms, value))
        


    y1_desc = str(cur_year-1)
    y2_desc = str(cur_year-2)
    y3_desc = str(cur_year-3)
    y4_desc = str(cur_year-4)
    y5_desc = str(cur_year-5)
    y6_desc = str(cur_year-6)
    y7_desc = str(cur_year-7)
    y8_desc = str(cur_year-8)
    
    drawdown = {
        str(cur_year):0, 
        y1_desc:0, 
        y2_desc:0,
        y3_desc:0,
        y4_desc:0,
        y5_desc:0,
        y6_desc:0,
        y7_desc:0,
        y8_desc:0,
    }
    
    # 输出分组结果
    
    for year, items in groups.items():

        _min = items[0][1]
        _min_date = items[0][0]
        _max = items[0][1]
        _max_date = items[0][0]
        
        g_length = len(items)
        
        huiches = []
        
        for i in range(2, g_length):
            dt = items[i][0]
            value = items[i][1]
            _max = 0

            for index,item in enumerate(items[:i]):
                dt2 = item[0]
                value2 = item[1]
                # 向左边找到最大值
                if value2 > _max:
                    _max = value2
                    _max_date = dt2

            # _max
            # print(f"min: {_min}, _min_date: {datetime.datetime.fromtimestamp(_min_date / 1000).date()}, ")
            
            huiches.append({
                'dt':dt,
                'dt2':datetime.fromtimestamp(dt / 1000).date(),
                'value':value,
                '_max':_max,
                '_max_date':_max_date,
                '_max_date2':datetime.fromtimestamp(_max_date / 1000).date(),
                'h':(_max-value)/_max*100,
            })

        huiches.sort(key=lambda x: x['h'], reverse=True)
        hc = huiches[0]
        # print(f"=== {year}:{hc['h']}， {hc['_max_date2']}， {hc['dt2']}===")

        drawdown[str(year)] = hc['h']
    # print(huiche)
    # {'2025': 9.031262060980314, '2024': 10.648918469217962, '2023': 16.27029067572669, '2022': 23.124999999999996, '2021': 13.413242009132425, '2020': 13.615384615384619, '2019': 11.470240441466297, '2018': 25.618576322801673, '2017': 5.298536971134832, '2013': 8.029878618113909, '2014': 8.596837944664028, '2015': 42.600896860986545, '2016': 19.94428969359331}
    
    # print("------")
    # print(drawdown)
    return drawdown


def tt_do_get_max_drawdown(_key:str, out_dir: str):
    fname = f"{out_dir}/{_key}-详情.xlsx"
    df = pd.read_excel(fname, dtype=str)
    

    datas = []
    num_rows = len(df)

    for index, row in df.iterrows():
        code = row["代码"]
        name = row["名称"]

        try:
            r = _tt_do_get_max_drawdown(code)
            s1 = f"处理完成:{num_rows}-{index+1}, {name}"
            _my_print(s1)
            
            d1 = row.to_dict()
  
            r2 = {}
            for k in r:
                r2[k+'回撤'] = r[k]
            
             
            d1.update(r2)
            
            datas.append(d1)
        except Exception as err:
            s1 = f"处理失败-----:{code}, {name}{err}"
            _my_print(s1)

    out = pd.DataFrame(datas)
    out.to_excel(f"{out_dir}/{_key}-详情-回撤.xlsx", index=False)
    out.to_csv(f"{out_dir}/{_key}-详情-回撤.csv", index=False)


def _calc_cur_bond_div_stock_bond()->float:
    # 十年期国债收益率
    # 地址先打开：https://quote.eastmoney.com/stock/171.CN10Y.html
    # 找到接口
    ntm = tm_get_13_timestamp()
    params = {
        'invt':'2',
        'fltt':'1',
        'cb':'jQuery35105820718960618639_'+str(ntm),
        'fields':'f43',
        'secid':'171.CN10Y',
        'ut':'fa5fd1943c7b386f172d6893dbfba10b',
        'dect':'1',
        'wbp2u':'|0|0|0|web',
        '_': str(ntm),

    }
    res = session.get('https://push2.eastmoney.com/api/qt/stock/get', params=params)

    txt = res.content.decode('utf8')
    m = re.search(r'\((.*)\)', txt, re.S)
    if m == None:
        return 0

    json_data = json.loads(m.group(1))
    snq = json_data['data']['f43'] / 10000
    # print('十年期国债:', snq)
    return snq

def _calc_cur_bond_div_stock_stock()->float:
    '''计算当前债股比'''
    
    ###### 
    txt = session.get('https://quote.eastmoney.com/newapi/sczm').content.decode('utf8')
    json_data = json.loads(txt)
    ss = json_data['ss']['ttm']
    cyb = json_data['cyb']['ttm']
    hs = json_data['hs']['ttm']
    # print('ss:', ss)
    # print('hs:', hs)
    # print('cyb:', cyb)
    avgv = ( ss+hs+cyb)/ 3
    # print('平均:',avgv)
    
    # v = 1/avgv*100/ snq
    # print('当前债股收益率比:', v)
    return avgv



def _get_page_bond_datas(page)->list:
    
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

    text = session.get(_url,params=params).content.decode('utf8')

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

    res = []
 
    for d in datas:
        s1 = d.replace(',','_')
        s = s1.replace('|',',')
        res.append(s)
    return res
    

def tt_do_get_bond_list(out_dir: str, fr:str):
    # all pages 
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
        'fr': fr,
        'plevel':'',
        'fst': '',
        'ftype':'',
        'fr1': '',
        'fl': '0',
        'isab': '',
    }

    text = session.get(_url,params=params).content.decode('utf8')
    all_pages = re.search(r'allPages\s*:\s*(\d+)', text).group(1)
    all_records = re.search(r'allRecords\s*:\s*(\d+)', text).group(1)

    all_pages = int(all_pages)
    s1 = f'债券基金所有页数为:{all_pages}, 总条数:{all_records}'
    _my_print(s1)


    ########## 
    fname = f"{out_dir}/bond_1.xlsx"

    if check_file_is_exist(fname):
        s1 = f'债券基金数据当日已经获取'
        _my_print(s1)
        return

    # 
    fname2 = f"{out_dir}/bond_1.csv"
    fname3 = f"{out_dir}/bond_1.json"

    fp1 = None
    if not check_file_is_exist(fname2):
        fp1 = open(fname2, mode='w', encoding='utf8')
        fp1.write('code,名称,类型,日期,净值,日增长率,近1周,近1月,近3月,近6月,近1年,近2年,近3年,今年来,成立来,f1,f2,f3,f4,f5,f6,f7,可购买,f9,起购金额,费率,e1,e2,e3\n')
    else:
        fp1 = open(fname2, mode='w', encoding='utf8')

    # start task
    task_status = {}
    task_status_raw = {}
    for i in range(1,all_pages+1):
        task_status[str(i)] = False
        task_status_raw[str(i)] = False

    if not check_file_is_exist(fname3):
        s2 = json.dumps(task_status)
        fp2 = open(fname3, mode='w', encoding='utf8')
        fp2.write(s2)
        fp2.close()
    else:
        fp2 = open(fname3, mode='r', encoding='utf8')
        txt = fp2.read()
        task_status = json.loads(txt)
        task_status_raw = json.loads(txt)
        fp2.close()
    
    
    has_excep = False
    for k in task_status:
        page = int(k)
        v = task_status[k]
        if bool(v):
            _my_print(f'当前页{page}已处理')
            continue
        
        try:
            _my_print(f'下载第{page}页')
            datas = _get_page_bond_datas(page)
            for d in datas:
                fp1.write(d)
                fp1.write('\n')
            
            task_status_raw[k] = True

        except Exception as err:
            _my_print(f'下载第{page}页,异常,{err}')
            task_status_raw[k] = False
            has_excep = True

        s2 = json.dumps(task_status_raw)
        fp_tmp = open(fname3, mode='w', encoding='utf8')
        fp_tmp.write(s2)
        fp_tmp.close()

    _my_print(f'下载完成')
    fp1.close()
    
    if has_excep:
        return

    df = pd.read_csv(fname2, dtype=str)
    df = df.drop(columns=["类型","日期","净值","日增长率", "f1", "f2", "f3", "f4", "f5", "f6", "f9","e1","e2","e3"])
    df.to_excel(f"{out_dir}/bond_1.xlsx", index=False)


if __name__ == '__main__':
    

    pass