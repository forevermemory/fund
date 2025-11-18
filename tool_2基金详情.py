import requests
import json
from lxml import etree
from bs4 import BeautifulSoup
import pandas as pd

session = requests.Session()


# https://fund.eastmoney.com/159513.html


def main():
    df = pd.read_csv('out2.csv')
    
    datas = []

    for index, row in df.iterrows():
 
        code = row["code"]
   
        _url = 'https://fundf10.eastmoney.com/jdzf_%s.html' % (code)
        res = session.get(_url)
        if res.status_code != 200:
            print("err ",res.status_code)
            return
        text = res.content.decode("utf8")
        
        ##### 
        html = etree.HTML(text)
        name = html.xpath('/html/body/div[1]/div[8]/div[3]/div[1]/div[1]/div[1]/h4/a/text()')[0].strip()
        基金经理 = html.xpath('/html/body/div[1]/div[8]/div[3]/div[1]/div[2]/p/label[2]/a/text()')[0].strip()
        规模 = html.xpath('/html/body/div[1]/div[8]/div[3]/div[1]/div[2]/p/label[5]/span/text()')[0].strip().split('\r\n')[0]
        成立日期 = html.xpath('/html/body/div[1]/div[8]/div[3]/div[1]/div[2]/p/label[1]/span/text()')[0].strip()
        单位净值 = html.xpath('/html/body/div[1]/div[8]/div[3]/div[1]/div[1]/div[2]/p[1]/label/b/text()')[0].strip()
        
        ### js call
        
        _url2 = 'https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jdzf&code=%s' % (code)
        res = session.get(_url2)
        if res.status_code != 200:
            print("err ",res.status_code)
            return
        text = res.content.decode("utf8")
        text2 = text.replace('var apidata={ content:"','').replace('"};','')
        
        soup = BeautifulSoup(text2, "lxml")
        uls = soup.select("div ul")

        
        近年来 = uls[2-1].find_all('li')[1].text
        近1周 = uls[3-1].find_all('li')[1].text
        近1月 = uls[4-1].find_all('li')[1].text
        近3月 = uls[5-1].find_all('li')[1].text
        近6月 = uls[6-1].find_all('li')[1].text
        近1年 = uls[7-1].find_all('li')[1].text
        近2年 = uls[8-1].find_all('li')[1].text
        近3年 = uls[9-1].find_all('li')[1].text
        近5年 = uls[10-1].find_all('li')[1].text
        成立来 = uls[11-1].find_all('li')[1].text
        
        print(code, name, 基金经理, 规模, 成立日期, 近年来, 近1周, 近1月, 近3月, 近6月, 近1年, 近2年, 近3年, 近5年, 成立来)
        
        d1 = {
            'code'          :code,
            'name'          :name,
            '基金经理'         :基金经理,
            '规模'          :规模,
            '成立日期'          :成立日期,
            '单位净值'          :单位净值,
            '近年来'          :近年来,
            '近1周'          :近1周,
            '近1月'          :近1月,
            '近3月'          :近3月,
            '近6月'          :近6月,
            '近1年'          :近1年,
            '近2年'          :近2年,
            '近3年'          :近3年,
            '近5年'          :近5年,
            '成立来'          :成立来,
        }
        datas.append(d1)
    
    out = pd.DataFrame(datas)
    out.to_excel("out3.xlsx", index=False)
    out.to_csv("out3.csv", index=False)
    pass
    
    
if __name__ == '__main__':
    main()
    
    pass