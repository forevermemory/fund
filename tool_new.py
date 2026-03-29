import time
import requests
import re
import json
import pandas as pd
from datetime import datetime,date
from bs4 import BeautifulSoup
from collections import defaultdict
import os

req_session = requests.Session() 
TIMEOUT=5


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


def parse_jsonp_response(data: str):
    m = re.search(r'\((.*)\)', data, re.S)
    if m == None:
        return None

    json_data = json.loads(m.group(1))
    return json_data

def _my_print(s:str):
    print(s)

def update_flag_get(s:str, key:str, v:str) -> bool:
    item = {}
    try:
        item = json.loads(s)
    except Exception as _:
        return False
    
    old = item.get(key) 
    if old is None:
        return False
    
    if old != v:
        return False

    return True

def update_flag_update(s:str, key:str, v:str) -> str:
    item = {}
    try:
        item = json.loads(s)
    except Exception as _:
        pass


    item[key] = v
    return json.dumps(item)

def s_date_calc_since_totay(s)->int:
    '''s:2009-07-21'''
    try:
        target = datetime.strptime(s, "%Y-%m-%d").date()
        today = date.today()

        delta_days = (today - target).days
        return delta_days
    except Exception as _:
        return 0

def s_to_float(s:str)->float:
    '''0.80%'''
    v = 0.00

    if s == None:
        return v

    if type(s) == float:
        return s

    if type(s) == int:
        return float(s)

    s2 = s.replace('%','')
    try:
        v = float(s2)
    except Exception as _:
        v = 0.00

    return v



def _tt_do_search_fund_item(code: str)->dict:
    now = str(int(time.time() * 1000))

    _url = 'https://fund.eastmoney.com/%s.html' % (code)

    r = req_session.get(_url, timeout=TIMEOUT)
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
            '类型': '',
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
            y0_desc: '',
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

    # 类型_r = trs[0].find_all('td')[0].text.replace('类型：', '')
    类型 = trs[0].find_all('td')[0].find('a').text

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
    y0 = 今年来
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
        '类型': 类型,
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
        y0_desc: y0,
        y1_desc: y1,
        y2_desc: y2,
        y3_desc: y3,
        y4_desc: y4,
        y5_desc: y5,
        y6_desc: y6,
        y7_desc: y7,
        y8_desc: y8,
    }
    
    # if b:
    #     b.nh_cur = 0.0 
    #     b.nh_1 = s_to_float(y1)
    #     b.nh_2 = s_to_float(y2)
    #     b.nh_3 = s_to_float(y3)
    #     b.nh_4 = s_to_float(y4)
    #     b.nh_5 = s_to_float(y5)
    #     b.nh_6 = s_to_float(y6)
    #     b.nh_7 = s_to_float(y7)
    #     b.nh_8 = s_to_float(y8)

    # print(data)
    return data



def _tt_do_search_fund_item_fenhong(code: str)->dict:
    '''分红'''
 
    _url = 'https://fundf10.eastmoney.com/fhsp_%s.html' % (code)
    r = req_session.get(_url, timeout=TIMEOUT)
    # 可能是后端，然后重定向

    text = r.content.decode('utf8')

    # fp = open('b.html', encoding='utf8')
    # text = fp.read()
    # fp.close()

    # html = etree.HTML(text)

    soup = BeautifulSoup(text, "lxml")
    # part1
    container_base = '#bodydiv > div:nth-child(13) > div.r_cont.right > div.detail > div.txt_cont > div > div:nth-child(2) > div > table > tbody > tr'
    trs = soup.select(container_base)
 

    tr1 = trs[0]
    tds = tr1.select('td')
    if len(tds) <=3:
        data = {
            '分红1': '无',
            '分红2': '无',
            '分红3': 0,
        }

        return data
    
    p1 = tds[1].text
    p2 = tds[3].text.replace('每份派现金','')
    data = {
        '分红1': p1,
        '分红2': p2,
        '分红3': len(trs),
    }
    



    return data



def _tt_do_search_fund_item_nianfei(code: str)->dict:
    '''年费'''
 
    _url = 'https://fundf10.eastmoney.com/jjfl_%s.html' % (code)
    r = req_session.get(_url, timeout=TIMEOUT)
    # 可能是后端，然后重定向

    text = r.content.decode('utf8')
 
    soup = BeautifulSoup(text, "lxml")
    # part1
    container_base = '#bodydiv > div:nth-child(12) > div.r_cont.right > div.detail > div.txt_cont > div > div:nth-child(4) > div > table > tbody > tr > td'
    tds = soup.select(container_base)

    data = {
        '管理费率': tds[1].text.replace('（每年）',''),
        '托管费率': tds[3].text.replace('（每年）',''),
    }
    # if b:
    #     b.feiyong1 = data['管理费率']
    #     b.feiyong2 = data['托管费率']
    return data




def _tt_do__max_drawdown(code:str) -> dict:
    '''获取某一只的年度最大回撤'''
    now = datetime.now()
    now_str = f'{now.year}{now.month}{now.day}{now.hour}{now.minute}{now.second}'
    _url = 'https://fund.eastmoney.com/pingzhongdata/%s.js?v=%s' % (code, now_str)
    
    # print(_url)
    r = req_session.get(_url, timeout=TIMEOUT)
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
        try:
        
            for i in range(2, g_length):
                dt = items[i][0]
                value = items[i][1]
                if value == None:
                    value = 0
                _max = 0

                for index,item in enumerate(items[:i]):
                    dt2 = item[0]
                    value2 = item[1]
                    if value2 == None:
                        value2=0
                    # 向左边找到最大值
                    if value2 > _max:
                        _max = value2
                        _max_date = dt2

                # _max
                # print(f"AAAA min: {_min}, _min_date: {datetime.fromtimestamp(_min_date / 1000).date()}, ")
                value = float(value)
                huiches.append({
                    'dt':dt,
                    'dt2':datetime.fromtimestamp(dt / 1000).date(),
                    'value':value,
                    '_max':_max,
                    '_max_date':_max_date,
                    '_max_date2':datetime.fromtimestamp(_max_date / 1000).date(),
                    # 'h':(_max-value)/_max*100,
                    'h': '%.2f' % float((_max-value)/_max*100),
                })

            huiches.sort(key=lambda x: x['h'], reverse=True)
            hc = huiches[0]
            # print(f"=== {year}:{hc['h']}， {hc['_max_date2']}， {hc['dt2']}===")
            drawdown[str(year)] = hc['h']
        except Exception as err:
            print("计算回撤失败:",year,_max,_max_date,value,dt,g_length, err)
    # print(huiche)

    # print(drawdown)
    # {'2026': '9.85', '2025': '9.83', '2024': '9.97', '2023': '9.66', '2022': '9.93', '2021': '5.67', '2020': '9.93', '2019': '6.31', '2018': '9.86'}

    return drawdown



def _tt_get_page_bond_datas(page)->list:
    
    dt = str(int(time.time() * 1000))
    _url = 'https://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx'
    params = {
        "t":"10",
        "lx":"4",
        "letter":"",
        "gsid":"",
        "text":"",
        "sort":"rzdf,desc",
        "page":f"{page},200",
        "feature":"|",
        "dt":dt,
        "atfc":"",
        "onlySale":"0",
        "isLatest":"0",
        "_":dt,
    }

    text = req_session.get(_url,params=params, timeout=TIMEOUT).content.decode('utf8')

    '''
    var db={
        chars:["a","b","c","d","f","g","h","j","k","l","m","n","p","q","r","s","t","w","x","y","z"],
        datas:[
            ["025400","南方昌元可转债债券B","","2.0337","2.0537","2.0078","2.0278","0.0259","1.29","开放申购","开放赎回","","1","0","1","","","0.09%","0.09%","","0.90%","03-27","03-26"],
            ["006030","南方昌元可转债债券A","","2.0346","2.0546","2.0087","2.0287","0.0259","1.29","开放申购","开放赎回","","1","0","2","","","0.08%","0.08%","","0.80%","03-27","03-26"]
            ],
        count:["0","0","0","0"],
        record:"7112",
        pages:"36",
        curpage:"1",
        indexsy:[0.63,0.56,1.13,],
        showday:["2026-03-27","2026-03-26"]
    }
    '''

    # all_pages = re.search(r'allPages\s*:\s*(\d+)', text).group(1)
    datas_str = re.search(r'datas:(.*?),count', text, re.S).group(1)
    # datas = re.findall(r'"(.*?)"', datas_str)

    obj = json.loads(datas_str)

    res = []
 
    # for d in obj:
    #     print(d)
        # ['040013', '华安强化收益债券B', '', '1.42', '2.2837', '1.4165', '2.2802', '0.0035', '0.25', '开放申购', '开放赎回', '', '1', '0', '400', '', '', '0.00%', '0.00%', '', '0.00%', '03-27', '03-26']

    # print(obj)
    return obj


def _tt_bond_get_all_page() -> tuple:
    # 点击方式： 全部基金 --> 选择债券型 \n https://fund.eastmoney.com/fund.html#os_0;isall_0;ft_;pt_1
    # https://fund.eastmoney.com/ZQ_jzzzl.html#os_0;isall_0;ft_;pt_4
    dt = str(int(time.time() * 1000))

    ### 获取总页数 
    _url = 'https://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx'
    params = {
        "t":"10",
        "lx":"4",
        "letter":"",
        "gsid":"",
        "text":"",
        "sort":"rzdf,desc",
        "page":"1,200",
        "feature":"|",
        "dt":dt,
        "atfc":"",
        "onlySale":"0",
        "isLatest":"0",
        "_":dt,
    }

    text = req_session.get(_url, params=params, timeout=TIMEOUT*2).content.decode('utf8')

    # print(text)
    # record:"7112",pages:"36",
    all_records = re.search(r'record:\"(\d+)\"', text).group(1)
    pages = re.search(r'pages:\"(\d+)\"', text).group(1)

    all_pages = int(pages)
    return (all_records,all_pages)
    # s1 = f'债券基金所有页数为:{all_pages}, 总条数:{all_records}'


def _tt_bond_get_all_page_v2() -> tuple:
    # 点击方式： 基金超市 --> 债券型
    # https://fund.eastmoney.com/trade/zq.html
    dt = str(int(time.time() * 1000))

    ### 获取总页数 
    _url = 'https://fund.eastmoney.com/data/fundtradenewapi.aspx'
    params = {
        "ft": "zq",
        "sc": "1n",
        "st": "desc",
        "pi": "2",
        "pn": "100",
        "cp": "",
        "ct": "",
        "cd": "",
        "ms": "",
        "fr": "",
        "plevel": "",
        "fst": "",
        "ftype": "",
        "fr1": "",
        "fl": "0",
        "isab": "1",
    }

    text = req_session.get(_url, params=params, timeout=TIMEOUT*2).content.decode('utf8')

    # print(text)
    '''
    var rankData = {
        datas: ["017771|华夏聚利债券C|债券型|2026-03-27|2.1204|0.34|0.64|-2.30|0.75|4.46|17.10|31.90|19.06|0.84|18.39|3|0|1|0.00|0||043|1|1|10元||0.00%||", "002405|光大中高等级债券A|债券型|2026-03-27|1.7878|0.27|0.77|-1.02|3.66|7.12|17.06|51.35|39.99|3.70|85.17|3|1|1|0.08|0||043|1|1|10元|0.80%|0.08%|0.08%|1", ],
        allRecords: 5906,
        pageIndex: 2,
        pageNum: 100,
        allPages: 60
    };

    '''

    all_pages = re.search(r'allPages\s*:\s*(\d+)', text).group(1)
    all_records = re.search(r'allRecords\s*:\s*(\d+)', text).group(1)

    all_pages = int(all_pages)
    # 总条数:5906
    s1 = f'债券基金所有页数为:{all_pages}, 总条数:{all_records}'
    print(s1)
    return (all_records,all_pages)


if __name__ == "__main__":
    res = _tt_do_search_fund_item("002765")
    print(res)