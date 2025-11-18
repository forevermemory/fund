import requests
import json
from lxml import etree
from bs4 import BeautifulSoup
import pandas as pd

session = requests.Session()


def main():
    # _url = 'https://fund.eastmoney.com/cnjy_jzzzl.html'
    # res = session.get(_url)
    # if res.status_code != 200:
    #     print("err ",res.status_code)
    #     return
    # text = res.content.decode("gb2312")
    
    # fp = open('a.html', mode='w', encoding='utf8')
    # fp.write(text)
    # fp.close()
    fp = open('b.html', mode='r', encoding='utf8')
    text = fp.read()
    fp.close()
 

    soup = BeautifulSoup(text, "lxml")
    trs = soup.select("tbody tr")
    
    # print(trs)
    
    datas = []
    print(len(trs))

    for tr in trs[2:]:
        tds = tr.find_all('td')
        
        try:
            code = tds[3].text
            j_type = tds[5].text
            price_prev_2_1 = tds[6].text
            price_prev_2_2 = tds[7].text
            price_prev_1_1 = tds[8].text
            price_prev_1_1 = tds[9].text
            price_cur = tds[12].text
            
            name = tds[4].find_all("a")[0].text
            
            datas.append({
                'code':code,
                'name':name,
            })

            print(code,name)
        except Exception as err:
            print(err)

    
    out = pd.DataFrame(datas)
    out.to_excel("out.xlsx", index=False)
    out.to_csv("out.csv", index=False)
    
    datas2 = []
    for d in datas:
        
        if d['name'].find('上证50') > 0:
            datas2.append(d)
            
    out = pd.DataFrame(datas2)
    out.to_excel("out2.xlsx", index=False)
    out.to_csv("out2.csv", index=False)
    
    
if __name__ == '__main__':
    main()
    
    pass