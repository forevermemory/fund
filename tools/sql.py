
from datetime import datetime

# 导入必要的模块
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Sequence,FLOAT

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def get_year_month_day() -> str:
    now = datetime.now()
    return f"{now.year}-{now.month}-{now.day}"

engine = create_engine('sqlite:///money.db')
# 使用 sessionmaker 创建一个会话类 Session，并绑定到数据库引擎（bind=engine）
_Session = sessionmaker(bind=engine)
# 创建一个实例化的会话对象 session
sql_session = _Session()


########## 
# 创建一个基类，用于定义数据模型的基本结构
Base = declarative_base()

# 定义一个数据模型类，对应数据库中的 'chenxing' 表
class Chenxing(Base):
    # 定义表名
    __tablename__ = 'chenxing'
 
    # 定义列：id，是整数类型，主键（primary_key=True），并使用 Sequence 生成唯一标识
    id = Column(Integer, Sequence('user_id_seq'), 
                primary_key=True, autoincrement="auto")
 
    # 定义列：name，是字符串类型，最大长度为50
    code = Column(String(50))
    cx_code = Column(String(50))
    name = Column(String(255))
    cate = Column(String(50))
 
    # # 定义列：age，是整数类型
    # age = Column(Integer)

class BondFund(Base):
    __tablename__ = 'bond_fund'
 
    id = Column(Integer, Sequence('id_seq'), 
                primary_key=True, autoincrement="auto")
 
    # 定义列：name，是字符串类型，最大长度为50
    code = Column(String(50), unique=True)
    name = Column(String(50))

# code	名称	近1周	近1月	近3月	近6月	近1年	近2年	近3年	今年来	成立来	可购买	起购金额	费率
    near_1w = Column(FLOAT)
    near_1m = Column(FLOAT)
    near_3m = Column(FLOAT)
    near_6m = Column(FLOAT)
    near_1y = Column(FLOAT)
    near_2y = Column(FLOAT)
    near_3y = Column(FLOAT)
    near_now_y = Column(FLOAT)
    near_all_y = Column(FLOAT)
    buy_rate = Column(FLOAT) # 

    update_flag = Column(String(50))

    establish_date = Column(Integer) # 成立日
    establish_day = Column(Integer) # 成立日
    total_money = Column(Integer) # 规模
    company = Column(String(50)) # 管理人
    manager = Column(String(50)) # 基金经理

    # 年化收益
    nh_cur = Column(FLOAT) 
    nh_1 = Column(FLOAT) 
    nh_2 = Column(FLOAT) 
    nh_3 = Column(FLOAT) 
    nh_4 = Column(FLOAT) 
    nh_5 = Column(FLOAT) 
    nh_6 = Column(FLOAT) 
    nh_7 = Column(FLOAT) 
    nh_8 = Column(FLOAT) 

    # 最大回撤
    hc_cur = Column(FLOAT) 
    hc_1 = Column(FLOAT) 
    hc_2 = Column(FLOAT) 
    hc_3 = Column(FLOAT) 
    hc_4 = Column(FLOAT) 
    hc_5 = Column(FLOAT) 
    hc_6 = Column(FLOAT) 
    hc_7 = Column(FLOAT) 
    hc_8 = Column(FLOAT) 

    # 近三年
    # standard deviation
    std_1 = Column(FLOAT) 
    std_2 = Column(FLOAT) 
    std_3 = Column(FLOAT) 

    # Sharpe Ratio
    sharpe_1 = Column(FLOAT) 
    sharpe_2 = Column(FLOAT) 
    sharpe_3 = Column(FLOAT) 




    # # 定义列：age，是整数类型
    # age = Column(Integer)

class Fund(Base):
    __tablename__ = 'fund'
 
    id = Column(Integer, Sequence('id_seq'), 
                primary_key=True, autoincrement="auto")
 
    # 定义列：name，是字符串类型，最大长度为50
    code = Column(String(50), unique=True)
    name = Column(String(50))

    # code	名称	近1周	近1月	近3月	近6月	近1年	近2年	近3年	今年来	成立来	可购买	起购金额	费率
    near_1w = Column(FLOAT)
    near_1m = Column(FLOAT)
    near_3m = Column(FLOAT)
    near_6m = Column(FLOAT)
    near_1y = Column(FLOAT)
    near_2y = Column(FLOAT)
    near_3y = Column(FLOAT)
    near_now_y = Column(FLOAT)
    near_all_y = Column(FLOAT)
    buy_rate = Column(FLOAT) # 

    update_flag = Column(String(50)) # date

    establish_date = Column(Integer) # 成立日
    establish_day = Column(Integer) # 成立日
    total_money = Column(Integer) # 规模
    company = Column(String(50)) # 管理人
    manager = Column(String(50)) # 基金经理
    nh_deviation = Column(String(50)) # 年化跟踪误差
    bd = Column(String(50)) # 跟踪标的
    trade_status = Column(String(50)) # 交易状态

    # 年化收益
    nh_cur = Column(FLOAT) 
    nh_1 = Column(FLOAT) 
    nh_2 = Column(FLOAT) 
    nh_3 = Column(FLOAT) 
    nh_4 = Column(FLOAT) 
    nh_5 = Column(FLOAT) 
    nh_6 = Column(FLOAT) 
    nh_7 = Column(FLOAT) 
    nh_8 = Column(FLOAT) 

    # 最大回撤
    hc_cur = Column(FLOAT) 
    hc_1 = Column(FLOAT) 
    hc_2 = Column(FLOAT) 
    hc_3 = Column(FLOAT) 
    hc_4 = Column(FLOAT) 
    hc_5 = Column(FLOAT) 
    hc_6 = Column(FLOAT) 
    hc_7 = Column(FLOAT) 
    hc_8 = Column(FLOAT) 

    # 近三年
    # standard deviation
    std_1 = Column(FLOAT) 
    std_2 = Column(FLOAT) 
    std_3 = Column(FLOAT) 

    # Sharpe Ratio
    sharpe_1 = Column(FLOAT) 
    sharpe_2 = Column(FLOAT) 
    sharpe_3 = Column(FLOAT) 

    feiyong1 = Column(String(50)) 
    feiyong2 = Column(String(50)) 
    
    fenhong1 = Column(String(50)) 
    fenhong2 = Column(String(50)) 
    fenhong3 = Column(String(50)) 




### 添加
### migrate
Base.metadata.create_all(engine)

# # 创建一个新的 User 实例，即要插入到数据库中的新用户
# new_user = User(name='John Doe', age=30)
 
# # 将新用户添加到会话中，即将其添加到数据库操作队列中
# session.add(new_user)
 
# # 提交会话，将所有在此会话中的数据库操作提交到数据库
# session.commit()



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

# def cx_data_init():
#     global _chenxing_code_kv
    
#     cursor.execute('select * from chenxing;')
#     datas = cursor.fetchall()
#     # 将 rows转换成 [{},{}]
#     cursor.close()
#     res = rows_to_dict(cursor.description, datas)
    
#     # [{'id': '1', 'phone': '13399999999', 'username': '超级测试人员'}, {'id': '2', 'phone': '18899999999', 'username': '测试'}]
#     for item in res:
#         _chenxing_code_kv[item['code']] = item['cx_code']


# def cx_get_code(code)->str:
#     global _chenxing_code_kv
#     return _chenxing_code_kv[code]

# def cx_add(code, cx_code, name, cate):
    
#     try:
#         cursor.execute('''INSERT INTO "chenxing"("id", "code", "cx_code", "name", "cate") 
#                     VALUES 
#             (NULL, '%s', '%s', '%s', '%s');''' % (
#                 code, cx_code, name, cate,
#             )
            
#             )
#         conn.commit()
#     except Exception as err:
#         print("\tinsert err ",err)



if __name__ == '__main__':

    # 使用查询语句
    # result = engine.execute('SELECT * FROM users')
    
    # 使用 ORM 查询接口
    chenxings = sql_session.query(Chenxing).all()

    # for c in chenxings:
    #     print(c.code,c.name)
    #     session.

    # cx_add()
    
#     import pandas as pd
#     df = pd.read_csv('out.csv', dtype=str)

#     # cx_data_init()
    
#     num_rows = len(df)
    
#     datas = {
        
#     }
# # code,name,link,fenlei,chengliriqi
# # 001322,东吴新趋势价值线灵活配置混合,https://www.morningstar.cn/quicktake/0P000165U9,行业股票-科技、传媒及通讯,2025-11-17
# # 515880,国泰中证全指通信设备ETF,https://www.morningstar.cn/quicktake/0P0001I2GB,行业股票-科技、传媒及通讯,2025-11-17
#     for index, row in df.iterrows():
        
#         code = row["code"]
#         name = row["name"]
#         fenlei = row["fenlei"]
#         cx_code = row["link"].split('/')[-1]
        
#         datas[code] = {
#             'code':code,
#             'name':name,
#             'fenlei':fenlei,
#             'cx_code':cx_code,
#         }


#     for k in datas:
#         item = datas[k]
#         code = item["code"]
#         name = item["name"]
#         fenlei = item["fenlei"]
#         cx_code = item["cx_code"]
        
#         try:
#             s1 = f"处理完成: {name}"
#             cx_add(code, cx_code, name, fenlei)
#             print(s1)

#         except Exception as err:
#             s1 = f"处理失败-----:{code}, {name}{err}"
#             print(s1)