import requests
import json
import re
from lxml import etree
from bs4 import BeautifulSoup
import pandas as pd
import time

session = requests.Session()



def do_search(code:str):
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
    part1 = soup.select(container_base+' > div.fundInfoItem > div.dataOfFund')

    # print(len(part1))
    if len(part1) == 0:
        container_base = '#body > div:nth-child(12) > div > div > div.fundDetail-main'
        part1 = soup.select(container_base+' > div.fundInfoItem > div.dataOfFund')


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
                    'y1': '',
                    'y2': '',
                    'y3': '',
                    'y4': '',
                    'y5': '',
                    'y6': '',
                    'y7': '',
                    'y8': '',
            }
        return data

    dls = part1[0].find_all('dl')
    # print(len(dls))

    dl_index = len(dls)-1
    累计净值 = ''
    累计净值 = dls[dl_index].find_all('dd')[0].find_all('span')[0].text
    成立来 = dls[dl_index].find_all('dd')[2].find_all('span')[1].text

    # print( 累计净值, 成立来)

  
    part2 = soup.select(container_base+" > div.fundInfoItem > div.infoOfFund > table")[0]
    trs = part2.find_all('tr')
    规模_r = trs[0].find_all('td')[1].text.replace('规模：','')
    规模 = re.sub(r'[\(（亿元（][^)]*[\)）]', '', 规模_r)

    基金经理 = trs[0].find_all('td')[2].find('a').text

    成立日 = trs[1].find_all('td')[0].text.replace('成 立 日','').replace('：','')
    管理人 = trs[1].find_all('td')[1].find('a').text

    # 这里可能数据缺失
    跟踪标的 = ''
    年化跟踪误差 = ''
    try:
        txt1 = trs[2].find_all('td')[0].text
        跟踪标的 = txt1.split('|')[0].replace('跟踪标的：','').strip()
        年化跟踪误差 = txt1.split('|')[1].replace('年化跟踪误差：','')
    except Exception as err:
        # print("==================跟踪缺失,", code)
        pass

    # print(规模, 基金经理, 成立日, 管理人, 跟踪标的, 年化跟踪误差)

    # 交易方式
    交易状态 = ''
    购买手续费 = ''
    pf1 = soup.select(container_base+" > div > div.buyWayWrap > div.buyWayStatic")
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

    y1_desc = niandu_desc[1].find('div').text
    y2_desc = niandu_desc[2].find('div').text
    y3_desc = niandu_desc[3].find('div').text
    y4_desc = niandu_desc[4].find('div').text
    y5_desc = niandu_desc[5].find('div').text
    y6_desc = niandu_desc[6].find('div').text
    y7_desc = niandu_desc[7].find('div').text
    y8_desc = niandu_desc[8].find('div').text

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
            'y1': y1,
            'y2': y2,
            'y3': y3,
            'y4': y4,
            'y5': y5,
            'y6': y6,
            'y7': y7,
            'y8': y8,
    }

    # print(data)
    return data

def main():

    df = pd.read_csv('out.csv', dtype=str)
    
    datas = []
    for index, row in df.iterrows():

        try:
 
            code = row["CODE"]
            name = row["NAME"]
            r1 = do_search(code)
            r1['名称'] = name
            datas.append(r1)
            print('处理完成:', index, name)
        except Exception as err:
            print('处理失败======',err, code, name)

    out = pd.DataFrame(datas)
    out.to_excel("out2.xlsx", index=False)
    out.to_csv("out2.csv", index=False)

if __name__ == '__main__':
    main()
    