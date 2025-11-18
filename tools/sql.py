

# INSERT INTO "main"."chenxing"("id", "code", "cx_code", "name", "cate") VALUES ('1', '1', '2', '3', '4');

import sqlite3
from datetime import datetime

# 连接数据库
conn = sqlite3.connect('D:\\dev\\spider\\baidu_user\\articles.db')
cursor = conn.cursor()
# 建表可以用 navicat


def rows_to_dict(descriptions: tuple, datas: tuple):
    '''datas descriptions 为 ((),())'''
    if descriptions == None:
        return None
    if len(datas) == 0:
        return []
    keys = [a[0] for a in descriptions]

    results = []
    for data in datas:
        # data 为tuple ()
        tmp = {}
        for _index, key in enumerate(keys):
            # 日期类型处理
            if isinstance(data[_index], datetime):
                tmp[key] = data[_index].strftime('%Y-%m-%d %H:%M:%S')
            else:
                tmp[key] = data[_index]
        results.append(tmp)
    return results


_chenxing_code_kv = {}

def cx_data_init():
    global _chenxing_code_kv
    
    cursor.execute('select * from chenxing;')
    datas = cursor.fetchall()
    # 将 rows转换成 [{},{}]
    cursor.close()
    res = rows_to_dict(cursor.description, datas)
    
    # [{'id': '1', 'phone': '13399999999', 'username': '超级测试人员'}, {'id': '2', 'phone': '18899999999', 'username': '测试'}]
    for item in res:
        _chenxing_code_kv[item['code']] = item['cx_code']


def cx_get_code(code)->str:
    global _chenxing_code_kv
    return _chenxing_code_kv[code]

def cx_add(code, cx_code, name, cate):
    
    try:
        cursor.execute('''INSERT INTO "chenxing"("id", "code", "cx_code", "name", "cate") 
                    VALUES 
            ('%s', '%s', '%s', '%s');''' % (
                code, cx_code, name, cate,
            )
            
            )
        conn.commit()
    except Exception as err:
        print("\tinsert err ",err)


if __name__ == '__main__':
    # cx_add()
    
    import pandas as pd
    df = pd.read_csv('')
    
    num_rows = len(df)
    
    datas = {
        
    }
# code,name,link,fenlei,chengliriqi
# 001322,东吴新趋势价值线灵活配置混合,https://www.morningstar.cn/quicktake/0P000165U9,行业股票-科技、传媒及通讯,2025-11-17
# 515880,国泰中证全指通信设备ETF,https://www.morningstar.cn/quicktake/0P0001I2GB,行业股票-科技、传媒及通讯,2025-11-17
    for index, row in df.iterrows():
        
        code = row["code"]
        name = row["name"]
        fenlei = row["fenlei"]
        cx_code = row["link"].split('/')[-1]
        
        datas[code] = {
            'code':code,
            'name':name,
            'fenlei':fenlei,
            'cx_code':code,
        }


    for item in datas:
        code = item["code"]
        name = item["name"]
        fenlei = item["fenlei"]
        cx_code = item["cx_code"]
        
        try:
            s1 = f"处理完成: {name}"
            cx_add(code, cx_code, name, fenlei)
            print(s1)

        except Exception as err:
            s1 = f"处理失败-----:{code}, {name}{err}"
            print(s1)