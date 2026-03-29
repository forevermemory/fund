import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QProgressBar
)
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject
from PyQt5.Qt import QMessageBox

from myglobal import state_manager
from myglobal import state_manager, is_valid_ip, NETWORK_MODE_DHCP, NETWORK_MODE_STATIC,get_user_home
from datetime import datetime
import time
import requests
import re
import json
import pandas as pd

from tool import get_year_month_day
from tool_new import s_date_calc_since_totay, s_to_float, update_flag_get, update_flag_update

from tool_new import _tt_do_search_fund_item, _tt_do_search_fund_item_fenhong, _tt_do_search_fund_item_nianfei,_tt_do__max_drawdown, _tt_bond_get_all_page,_tt_get_page_bond_datas
from sql import sql_session, Fund, Bond
from myglobal import FUND_INFO_BASIC,FUND_INFO_FEE,FUND_INFO_DRAWDOWN,FUND_INFO_FENHONG
from myglobal import BOND_INFO_DETAIL,BOND_INFO_LIST

req_session = requests.Session() 


# 用于线程安全更新UI
class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(str, state_manager)

    search_task_finished = pyqtSignal(list)
    has_new_version = pyqtSignal(str)

    ### 
    search_fund_list = pyqtSignal(list)
    search_fund_item = pyqtSignal(dict)


# ------------------- Worker -------------------

# ------------------- Worker -------------------
class Worker_Search(QRunnable):
    """轻量Worker，无状态，执行任务"""

    def __init__(self, params=dict):
        super().__init__()
        self.signals = WorkerSignals()
        self.is_running = True
        self.params = params

    def my_print(self, s: str):
        self.signals.log.emit(f"{s}")


    def _run(self):
        devices = []

        key = self.params.get('key')
        out_dir = self.params.get('out_dir')
        now = str(int(time.time() * 1000))

        ##### step1
        params = {
            'callback': 'jQuery18308932037864680957_1762998769877',
            'm': '0',
            'key': key,
            '_': now,
        }
        _url = 'https://fundsuggest.eastmoney.com/FundSearch/api/FundSearchPageAPI.ashx'

        self.my_print("first search start:")

        r = req_session.get(_url, params=params)
        r.encoding = "utf-8"
        m = re.search(r'\((.*)\)', r.text, re.S)
        if m is None:
            self.my_print("未知的数据类型")
            return

        json_data = json.loads(m.group(1))
        if json_data['ErrCode'] != 0:
            self.my_print("ErrCode")
            return

        data = json_data['Datas']  # {}
        items = data['FundList']
        page_size = len(data['FundList'])
        page_total = data['FundListTotalCount']

        s1 = "first search: %d - %d" % (page_size, page_total)
        self.my_print(s1)

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
            self.my_print(s1)
            r = req_session.get(_url, params=params)
            r.encoding = "utf-8"
            m = re.search(r'\((.*)\)', r.text, re.S)
            if m is None:
                self.my_print("未知的数据类型")
                return

            json_data = json.loads(m.group(1))
            if json_data['ErrCode'] != 0:
                self.my_print("ErrCode")
                return

            items = json_data['Datas']
            s1 = '累计数据:%d' % (len(items))
            self.my_print(s1)

        self.my_print("写入excel")
        out = pd.DataFrame(items)
        out.to_excel(f"{out_dir}/{key}_all.xlsx", index=False)
        self.signals.search_fund_list.emit(items)

    def run(self):
        #####
        try:
            self._run()
        except Exception as err:
            self.my_print(f"err:{err}")


class Worker_Fund(QRunnable):

    def __init__(self, params=dict):
        super().__init__()
        self.signals = WorkerSignals()
        self.is_running = True
        self.params = params

        self.today_str = ''
        self.cur_year = 0


    def my_print(self, s: str):
        self.signals.log.emit(f"{s}")

    def _get_fenhong(self, code:str, name:str, total, index):
        cur_year = self.cur_year
        today_str = self.today_str

        # check is exist
        is_exist = False
        b = sql_session.query(Fund).filter_by(code=code).first()
        if b:
            is_exist = True
            # if b.update_flag == today_str:
            #     continue
            if update_flag_get(b.update_flag, "fenhong", today_str):
                return
        else:
            b = Fund()

        t1 = update_flag_update(b.update_flag, "fenhong", today_str)
        b.update_flag = t1

        res = {

        }
        try:
            r1 = _tt_do_search_fund_item_fenhong(code)
            res.update(r1)
            s1 = f"处理分红完成:{total}-{index+1}, {name}"
            self.my_print(s1)

        except Exception as err:
            s1 = f"处理分红失败-----:{code}, {name}, {err}"
            self.my_print(s1)

        self.signals.search_fund_item.emit(res)

        ### to db 
        b.code = code
        b.name = name
        # data = {
        #     '分红1': p1,
        #     '分红2': p2,
        #     '分红3': len(trs),
        # }

        b.fenhong1 = res.get('分红1', '无')
        b.fenhong2 = res.get('分红2', '无')
        b.fenhong3 = res.get('分红3', '无')
        if not is_exist:
            sql_session.add(b)
        sql_session.commit()

    def _get_drawdown(self, code:str, name:str, total, index):
        cur_year = self.cur_year
        today_str = self.today_str
        # check is exist
        is_exist = False
        b = sql_session.query(Fund).filter_by(code=code).first()
        if b:
            is_exist = True
            # if b.update_flag == today_str:
            #     continue
            if update_flag_get(b.update_flag, "drawdown", today_str):
                return
        else:
            b = Fund()

        t1 = update_flag_update(b.update_flag, "drawdown", today_str)
        b.update_flag = t1

        res = {

        }
        try:
            r1 = _tt_do__max_drawdown(code)
            res.update(r1)
            s1 = f"处理回撤完成:{total}-{index+1}, {name}"
            self.my_print(s1)

        except Exception as err:
            s1 = f"处理回撤失败-----:{code}, {name}, {err}"
            self.my_print(s1)

        self.signals.search_fund_item.emit(res)

        ### to db 
        b.code = code
        b.name = name

        b.hc_cur = s_to_float(res.get(str(cur_year)))
        b.hc_1 = s_to_float(res.get(str(cur_year-1)))
        b.hc_2 = s_to_float(res.get(str(cur_year-2)))
        b.hc_3 = s_to_float(res.get(str(cur_year-3)))
        b.hc_4 = s_to_float(res.get(str(cur_year-4)))
        b.hc_5 = s_to_float(res.get(str(cur_year-5)))
        b.hc_6 = s_to_float(res.get(str(cur_year-6)))
        b.hc_7 = s_to_float(res.get(str(cur_year-7)))
        b.hc_8 = s_to_float(res.get(str(cur_year-8)))

        if not is_exist:
            sql_session.add(b)
        sql_session.commit()


    def _get_fee(self, code:str, name:str, total, index):
        cur_year = self.cur_year
        today_str = self.today_str
        # check is exist
        is_exist = False
        b = sql_session.query(Fund).filter_by(code=code).first()
        if b:
            is_exist = True
            # if b.update_flag == today_str:
            #     continue
            if update_flag_get(b.update_flag, "fee", today_str):
                return
        else:
            b = Fund()

        t1 = update_flag_update(b.update_flag, "fee", today_str)
        b.update_flag = t1

        res = {

        }
        try:
            r1 = _tt_do_search_fund_item_nianfei(code)
            res.update(r1)
            s1 = f"处理费用完成:{total}-{index+1}, {name}"
            self.my_print(s1)

        except Exception as err:
            s1 = f"处理费用失败-----:{code}, {name}, {err}"
            self.my_print(s1)

        self.signals.search_fund_item.emit(res)

        ### to db 
        b.code = code
        b.name = name

        b.feiyong1 = res.get('管理费率', '无')
        b.feiyong2 = res.get('托管费率', '无')
        if not is_exist:
            sql_session.add(b)
        sql_session.commit()


    def _get_basic(self, code:str, name:str, total, index):

        cur_year = self.cur_year

        # check is exist
        is_exist = False
        b = sql_session.query(Fund).filter_by(code=code).first()
        if b:
            is_exist = True
            # if b.update_flag == today_str:
            #     continue
            if update_flag_get(b.update_flag, "basic", self.today_str):
                return
        else:
            b = Fund()

        t1 = update_flag_update(b.update_flag, "basic", self.today_str)
        b.update_flag = t1

        res = {

        }
        try:
            r1 = _tt_do_search_fund_item(code)
            r1['名称'] = name
            res.update(r1)
            s1 = f"处理basic完成:{total}-{index+1}, {name}"
            self.my_print(s1)

        except Exception as err:
            s1 = f"处理basic失败-----:{code}, {name}, {err}"
            self.my_print(s1)

        self.signals.search_fund_item.emit(res)

        ### to db 
        b.code = code
        b.name = name

        b.near_1w = s_to_float(res["近1周"])
        b.near_1m = s_to_float(res["近1月"])
        b.near_3m = s_to_float(res["近3月"])
        b.near_6m = s_to_float(res["近6月"])
        b.near_1y = s_to_float(res["近1年"])
        b.near_2y = s_to_float(res["近2年"])
        b.near_3y = s_to_float(res["近3年"])
        b.near_now_y = s_to_float(res["今年来"])
        b.near_all_y = s_to_float(res["成立来"])
        b.buy_rate = 0.0

        b.establish_date = res["成立日"]
        b.establish_day = s_date_calc_since_totay(res['成立日'])
        b.total_money =res["规模"]
        b.company = res["管理人"]
        b.manager = res["基金经理"]
        b.nh_deviation = res["年化跟踪误差"]
        b.bd = res["跟踪标的"]
        b.trade_status = res["交易状态"]

        # 年化收益\
        b.nh_cur = s_to_float(res.get(str(cur_year)))
        b.nh_1 = s_to_float(res.get(str(cur_year-1)))
        b.nh_2 = s_to_float(res.get(str(cur_year-2)))
        b.nh_3 = s_to_float(res.get(str(cur_year-3)))
        b.nh_4 = s_to_float(res.get(str(cur_year-4)))
        b.nh_5 = s_to_float(res.get(str(cur_year-5)))
        b.nh_6 = s_to_float(res.get(str(cur_year-6)))
        b.nh_7 = s_to_float(res.get(str(cur_year-7)))
        b.nh_8 = s_to_float(res.get(str(cur_year-8)))
        # 最大回撤
        b.hc_cur = 0.0 

        # 近三年
        # standard deviation
        b.std_1 = 0.0
        b.std_2 = 0.0
        b.std_3 = 0.0

        # Sharpe Ratio
        b.sharpe_1 = 0.0
        b.sharpe_2 = 0.0
        b.sharpe_3 = 0.0
        
        if not is_exist:
            sql_session.add(b)
        sql_session.commit()

    def run(self):

        _key = self.params.get('key')
        out_dir = self.params.get('out_dir')
        cur_funds = self.params.get('cur_funds')
        mode = self.params.get('mode')

        now = str(int(time.time() * 1000))
        datas = [] 
        self.today_str = get_year_month_day()
        self.cur_year = datetime.now().year
          
        total = len(cur_funds)
        for index,item in enumerate(cur_funds):
            code = item["CODE"]
            name = item["NAME"]
            self.my_print(f"正在处理:{code}-{name}")

            try:
                if mode == FUND_INFO_BASIC:
                    self._get_basic(code, name, total, index)
                elif mode == FUND_INFO_FEE:
                    self._get_fee(code, name, total, index)
                elif mode == FUND_INFO_DRAWDOWN:
                    self._get_drawdown(code, name, total, index)
                elif mode == FUND_INFO_FENHONG:
                    self._get_fenhong(code, name, total, index)
                
            except Exception as err:
                self.my_print(f"处理失败:{code}-{name}")




class Worker_Fund_Export(QRunnable):

    def __init__(self, params=dict):
        super().__init__()
        self.signals = WorkerSignals()
        self.is_running = True
        self.params = params

    def my_print(self, s: str):
        self.signals.log.emit(f"{s}")

    def run(self):
        _key = self.params.get('key')
        out_dir = self.params.get('out_dir')
        cur_funds = self.params.get('cur_funds')

        now = str(int(time.time() * 1000))
        datas = [] 
        today_str = get_year_month_day()

        cur_year = datetime.now().year

        codes = []
        for index,item in enumerate(cur_funds):
            code = item["CODE"]
            codes.append(code)
        _s = ''
        for i in codes:
            _s+=f"'{i}',"
        _s+="'0'"
        df = pd.read_sql(f'select * from fund where code in ({_s})', sql_session.connection())

        # 处理ABCDE
        # df['total_money'] = df['total_money'].astype(float)
        # df["base"] = df['name'].str.replace(r"[ABCDE]$", "", regex=True)
        # agg = df.groupby("base")['total_money'].sum().reset_index()
        # df_a = df[df['name'].str.endswith("A")].copy()
        # df_a = df_a.merge(agg, 
        #                 on="base", 
        #                 suffixes=("", "_合并"))
        
        # # df_a.drop('base')

        # # 想移动的列
        # col = "total_money_合并"
        # cols = list(df_a.columns)
        # cols.insert(cols.index("total_money") + 1, col)
        # # 重排
        # df_a = df_a[cols[:-2]]

        fname = f"{out_dir}/{_key}_导出.xlsx"
        df.to_excel(fname, index=False)

        self.my_print(f'导出完成:{fname}')



class Worker_Bond(QRunnable):

    def __init__(self, params=dict):
        super().__init__()
        self.signals = WorkerSignals()
        self.is_running = True
        self.params = params
        self.today_str = get_year_month_day()

    def my_print(self, s: str):
        self.signals.log.emit(f"{s}")

    def _bond_list(self):

        now = str(int(time.time() * 1000))
        datas = [] 
        today_str = get_year_month_day()
        cur_year = datetime.now().year

        all_records,all_pages = _tt_bond_get_all_page()
        self.my_print(f'债券基金所有页数为:{all_pages}, 总条数:{all_records}')

        for i in range(all_pages):
            page = i+1

            self.my_print(f"获取第{all_pages}-{page}页数据")
            items = _tt_get_page_bond_datas(page)

            for item in items:
# ['040013', '华安强化收益债券B', '', '1.42', '2.2837', '1.4165', '2.2802', '0.0035', '0.25', '开放申购', '开放赎回', '', '1', '0', '400', '', '', '0.00%', '0.00%', '', '0.00%', '03-27', '03-26']

                code = item[0]
                name = item[1]
                status_buy = item[9]
                status_sale = item[10]

                # check is exist
                b = sql_session.query(Bond).filter_by(code=code).first()
                if b:
                    continue
                    # if update_flag_get(b.update_flag, "fenhong", today_str):
                    #     return
                else:
                    b = Bond()

                b.code = code
                b.name = name
                b.status_buy = status_buy
                b.status_sale = status_sale

                sql_session.add(b)
                sql_session.commit()



    def _bond_detail(self):
        bonds = sql_session.query(Bond).all()
        self.today_str = get_year_month_day()
        today_str = self.today_str
        cur_year = datetime.now().year

        total = len(bonds)

        self.my_print(f"累计:{total}")

        for index,b in enumerate(bonds):
            code = b.code
            name = b.name

            # check is exist
            is_exist = False
            b = sql_session.query(Bond).filter_by(code=code).first()
            if b:
                is_exist = True
                # if b.update_flag == today_str:
                #     continue
                if update_flag_get(b.update_flag, "basic", self.today_str):
                    return
            else:
                b = Bond()

            t1 = update_flag_update(b.update_flag, "basic", self.today_str)
            b.update_flag = t1

            res = {

            }
            try:
                r1 = _tt_do_search_fund_item(code)
                r1['名称'] = name
                res.update(r1)
                s1 = f"处理basic完成:{total}-{index+1}, {name}"
                self.my_print(s1)

            except Exception as err:
                s1 = f"处理basic失败-----:{code}, {name}, {err}"
                self.my_print(s1)

            self.signals.search_fund_item.emit(res)

            ### to db 
            b.code = code
            b.name = name

            b.near_1w = s_to_float(res["近1周"])
            b.near_1m = s_to_float(res["近1月"])
            b.near_3m = s_to_float(res["近3月"])
            b.near_6m = s_to_float(res["近6月"])
            b.near_1y = s_to_float(res["近1年"])
            b.near_2y = s_to_float(res["近2年"])
            b.near_3y = s_to_float(res["近3年"])
            b.near_now_y = s_to_float(res["今年来"])
            b.near_all_y = s_to_float(res["成立来"])
            b.buy_rate = 0.0

            b.establish_date = res["成立日"]
            b.establish_day = s_date_calc_since_totay(res['成立日'])
            b.total_money =res["规模"]
            b.kind =res["类型"]
            b.company = res["管理人"]
            b.manager = res["基金经理"]
            # b.nh_deviation = res["年化跟踪误差"]
            # b.bd = res["跟踪标的"]
            # b.trade_status = res["交易状态"]

            # 年化收益\
            b.nh_cur = s_to_float(res.get(str(cur_year)))
            b.nh_1 = s_to_float(res.get(str(cur_year-1)))
            b.nh_2 = s_to_float(res.get(str(cur_year-2)))
            b.nh_3 = s_to_float(res.get(str(cur_year-3)))
            b.nh_4 = s_to_float(res.get(str(cur_year-4)))
            b.nh_5 = s_to_float(res.get(str(cur_year-5)))
            b.nh_6 = s_to_float(res.get(str(cur_year-6)))
            b.nh_7 = s_to_float(res.get(str(cur_year-7)))
            b.nh_8 = s_to_float(res.get(str(cur_year-8)))
            # 最大回撤
            b.hc_cur = 0.0 

            # 近三年
            # standard deviation
            b.std_1 = 0.0
            b.std_2 = 0.0
            b.std_3 = 0.0

            # Sharpe Ratio
            b.sharpe_1 = 0.0
            b.sharpe_2 = 0.0
            b.sharpe_3 = 0.0
            
            if not is_exist:
                sql_session.add(b)
            sql_session.commit()

    def run(self):
        _key = self.params.get('key')
        out_dir = self.params.get('out_dir')
        cur_funds = self.params.get('cur_funds')
        mode = self.params.get('mode')

        try:
            if mode == BOND_INFO_LIST:
                self._bond_list()
            elif mode == BOND_INFO_DETAIL:
                self._bond_detail()
        except Exception as err:
            self.my_print(f"err:{err}")

# ------------------- 状态管理器 -------------------
class TaskManager:
    """管理任务状态，生成Worker"""
    def __init__(self):
        self.workers = {} # {task_id: state_manager}

    def get_worker_connect(self, task_id, work_params:dict):
        
        exist_state = self.workers.get(task_id)
        if exist_state is None:
            exist_state = state_manager()
            exist_state.ssh_params = work_params
            
            self.workers[task_id] = exist_state 
        
        # 使用新的参数
        exist_state.ssh_params = work_params
        
        # worker = Worker_Connect(task_id, state=exist_state)
        # 任务完成后更新状态
        # worker.signals.finished.connect(lambda w=worker: self._update_state(task_id, w.state))
        # return worker
    

    def get_worker_search(self, params:dict):
        worker = Worker_Search(params)
        return worker
    

    def get_worker_fund(self, params:dict):
        worker = Worker_Fund(params)
        return worker
    
    def get_worker_export(self, params:dict):
        worker = Worker_Fund_Export(params=params)
        return worker

    def get_worker_bond(self, params:dict):
        worker = Worker_Bond(params=params)
        return worker


