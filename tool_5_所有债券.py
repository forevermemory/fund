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

def s_to_float(s:str)->float:
    '''0.80%'''
    v = 0.00

    if s == None:
        return v


    s2 = s.replace('%','')
    try:
        v = float(s2)
    except Exception as _:
        v = 0.00

    return v


from tools.tool import s_date_2_to_13_timestamp,s_date_calc_since_totay
from tools.tool import _tt_do_get_max_drawdown

def main():
    
    # total = _get_total_page()
    # total = int(total)
    # for i in range(1,total+1):

    #     print(f'download:{total}-{i}')
    #     _get_page_datas(i)
    #     time.sleep(1)

    # fp1.close()
    # save
    # out = pd.DataFrame(outs)
    # # out.to_excel("国内指数.xlsx", index=False)
    # out.to_csv("中债指数-结果.csv", index=False)

    # step read excel
    df = pd.read_excel('bond_1.xlsx', sheet_name='输出', dtype=str)
    df = df.fillna(0)

    datas = []
    num_rows = len(df)

    from tools.sql import BondFund,session
    from tools.tool import _tt_do_search_fund_item

# code	名称	近1周	近1月	近3月	近6月	近1年	近2年	近3年	今年来	成立来	可购买	起购金额	费率
    # for index, row in df.iterrows():
    #     b = BondFund()
    #     b.code = row["code"]
    #     b.name = row["名称"]
    #     b.near_1w = s_to_float(row["近1周"])
    #     b.near_1m = s_to_float(row["近1月"])
    #     b.near_3m = s_to_float(row["近3月"])
    #     b.near_6m = s_to_float(row["近6月"])
    #     b.near_1y = s_to_float(row["近1年"])
    #     b.near_2y = s_to_float(row["近2年"])
    #     b.near_3y = s_to_float(row["近3年"])
    #     b.near_now_y = s_to_float(row["今年来"])
    #     b.near_all_y = s_to_float(row["成立来"])
    #     b.buy_rate = s_to_float(row["费率"])
    #     b.update_flag = '0'


    #     b.establish_date = ''
    #     b.total_money = 0.0
    #     b.company = ''
    #     b.manager = ''

    #     # 年化收益
    #     b.nh_cur = 0.0 
    #     b.nh_1 = 0.0 
    #     b.nh_2 = 0.0 
    #     b.nh_3 = 0.0 
    #     b.nh_4 = 0.0 
    #     b.nh_5 = 0.0 
    #     b.nh_6 = 0.0 
    #     b.nh_7 = 0.0 
    #     b.nh_8 = 0.0 

    #     # 最大回撤
    #     b.hc_cur = 0.0 
    #     b.hc_1 = 0.0 
    #     b.hc_2 = 0.0 
    #     b.hc_3 = 0.0 
    #     b.hc_4 = 0.0 
    #     b.hc_5 = 0.0 
    #     b.hc_6 = 0.0 
    #     b.hc_7 = 0.0 
    #     b.hc_8 = 0.0 

    #     # 近三年
    #     # standard deviation
    #     b.std_1 = 0.0
    #     b.std_2 = 0.0
    #     b.std_3 = 0.0

    #     # Sharpe Ratio
    #     b.sharpe_1 = 0.0
    #     b.sharpe_2 = 0.0
    #     b.sharpe_3 = 0.0
        
    #     print(b.name,b.buy_rate, b.near_3y)
    #     session.add(b)
    #     session.commit()
        

    fonds = session.query(BondFund).all()
    length = len(fonds)

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

    for i,f in enumerate(fonds):
        # if f.update_flag == '1':
        #     continue
        # print(f"处理:{length}-{i}-{f.name}")
        # res = _tt_do_search_fund_item(f.code)

        # f.total_money = res['规模']
        # f.manager = res['基金经理']
        # f.company = res['管理人']
        # f.establish_date = s_date_2_to_13_timestamp(res['成立日'])
        # f.establish_day = s_date_calc_since_totay(res['成立日'])
        # f.update_flag = '1'
        # # f.nh_cur = s_to_float(res[y0_desc])
        # f.nh_1 = s_to_float(res[y1_desc])
        # f.nh_2 = s_to_float(res[y2_desc])
        # f.nh_3 = s_to_float(res[y3_desc])
        # f.nh_4 = s_to_float(res[y4_desc])
        # f.nh_5 = s_to_float(res[y5_desc])
        # f.nh_6 = s_to_float(res[y6_desc])
        # f.nh_7 = s_to_float(res[y7_desc])
        # f.nh_8 = s_to_float(res[y8_desc])


    
        if f.update_flag == '2':
            continue
        print(f"处理:{length}-{i}-{f.name}")
        try:
            res = _tt_do_get_max_drawdown(f.code)
            if res == None:
                continue
            f.hc_cur = s_to_float(res[y0_desc])
            f.hc_1 = s_to_float(res[y1_desc])
            f.hc_2 = s_to_float(res[y2_desc])
            f.hc_3 = s_to_float(res[y3_desc])
            f.hc_4 = s_to_float(res[y4_desc])
            f.hc_5 = s_to_float(res[y5_desc])
            f.hc_6 = s_to_float(res[y6_desc])
            f.hc_7 = s_to_float(res[y7_desc])
            f.hc_8 = res[y8_desc]
            f.update_flag = '2'
            session.commit()     # 自动检测到变化
        except Exception as err:
            print(err)

if __name__ == '__main__':
    main()