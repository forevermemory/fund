
import sys
import time
from mainwindow import Ui_MainWindow

from PyQt5.Qt import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThreadPool, QThread, Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout, QPushButton, QMainWindow

from tool_new import check_dir,check_file_is_exist, get_year_month_day
from worker import TaskManager
import os
import platform
import subprocess
import pandas as pd
from myglobal import FUND_INFO_BASIC,FUND_INFO_FEE,FUND_INFO_DRAWDOWN,FUND_INFO_FENHONG
from myglobal import BOND_INFO_LIST,BOND_INFO_DETAIL


class Window(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("wwwww")

        self.items_code = {} # code -- 路径
        self.items_name = {} # name -- 路径
        self.items_name_code = {} # name -- code
        self.items_code_name = {} # code -- name

        ### data
        self.cur_funds = [] 

        # 线程池
        self.pool = QThreadPool()
        self.pool.setMaxThreadCount(50)
        self.work_mgr = TaskManager()

        ### ui
        self.init_ui()  # 界面绘制交给InitUi方法

        # tool.log_init(self.m_log)
        self.m_tt_input_zhishu_name.setText('纳斯达克')

        # self._print_txt('晨星数据加载中')
        # # sql.cx_data_init()
        # self._print_txt('晨星数据加载完成')
        
        self._load_datas()

    def init_ui(self):
        self.setupUi(self)

        # 创建目录
        check_dir("datas")
        # os.path.join(os.getcwd(), "images", 'xxx')
        check_dir(self._get_today_dir())

        # 搜索指数列表
        self.m_tt_funds.cellClicked.connect(self.on_m_tt_funds_cellClicked)
        

    def _get_today_dir(self)->str:
        return "datas/"+get_year_month_day()

    def _print_txt(self, s):
        self.m_log.append(s)

    # def _table_item_click(self, row, col):
    #     self.m_log.append(f'{row}-{col}')
    #     if col == 0:
    #         self.m_tt_funds.removeRow(row)
    #     self.m_tt_fund_info.setText(f"累计:{self.m_tt_funds.rowCount()}")

    ########## 加载数据
    def _load_datas(self):
        self._load_data_zhongzhaizhishu()
        self._load_data_tt_bond_fund_tp()


        self.m_tt_funds.setHorizontalHeaderItem(0, QTableWidgetItem('移除'))
        self.m_tt_funds.setHorizontalHeaderItem(1, QTableWidgetItem('代码'))
        self.m_tt_funds.setHorizontalHeaderItem(2, QTableWidgetItem('名称'))
        self.m_tt_funds.setColumnWidth(0, 40)
        self.m_tt_funds.setColumnWidth(1, 80)
        self.m_tt_funds.setColumnWidth(2, 360)
        self.m_tt_funds.verticalHeader().setVisible(False)

        self.m_tt_fund_info.setText(f"累计:0")

        # self.m_tt_ck_fenhong.setChecked(True)



    def _load_data_tt_bond_fund_tp(self):
        self.m_tt_bond_tp.setMaxVisibleItems(10)
        self.m_tt_bond_tp.addItem('所有类型', '')
        self.m_tt_bond_tp.addItem('长期纯债', '041')
        self.m_tt_bond_tp.addItem('短期纯债', '042')
        self.m_tt_bond_tp.addItem('混合债', '043')
        self.m_tt_bond_tp.addItem('定开债', '044')
        self.m_tt_bond_tp.addItem('定开债2', '071')
        self.m_tt_bond_tp.addItem('可转债', '055')
        # "041": "长期纯债",
        # "042": "短期纯债",
        # "043": "混合债",
        # "044": "定开债",
        # "071": "定开债",
        # "045": "可转债",
    
    def _load_data_zhongzhaizhishu(self):

        self.m_comb_zz_show_list.setMaxVisibleItems(30)

        fp = open('data/中债指数.txt', mode='r', encoding='utf8')
        txt = fp.read()
        fp.close()
        
        items = txt.split('\n')
        for item in items:
            name_code = item.split(',')
            name = name_code[0].replace('中债-', '')
            self.m_comb_zz_show_list.addItem(name, name_code[1])


    ################### 信号
    # @pyqtSlot()

    def on_m_tt_funds_cellClicked(self, row, col):
        self._print_txt(f'{row}-{col}')

        if col == 0:
            self.m_tt_funds.removeRow(row)
            # 移除当前选中的item

        self.m_tt_fund_info.setText(f"累计:{self.m_tt_funds.rowCount()}")


    @pyqtSlot()
    def on_m_tt_btn_opendir_clicked(self):
        folder_path = self._get_today_dir()
        abs_path = os.path.join('.', folder_path)
        print(abs_path)
        if platform.system() == 'Windows':
            os.startfile(abs_path)
        else:
            subprocess.run(['open', abs_path])
            
    @pyqtSlot()
    def on_m_tt_btn_fund_cond_clicked(self):
        cond = self.m_tt_fund_cond.text()
        if cond == '':
            return

        tmp = []
        total = self.m_tt_funds.rowCount()
        for i in range(total):
            txt = self.m_tt_funds.item(i, 2).text()
            if txt.find(cond) == -1:
                continue
            tmp.append(i)

        # update
        tmp2 = list(reversed(tmp))
        for i in tmp2:
            self.m_tt_funds.removeRow(i)
        self.m_tt_fund_info.setText(f"累计:{self.m_tt_funds.rowCount()}")

        ##### to excel
        tmp = []
        total = self.m_tt_funds.rowCount()
        for i in range(total):
            code = self.m_tt_funds.item(i, 1).text()
            name = self.m_tt_funds.item(i, 2).text()
            tmp.append({'CODE': code, 'NAME': name})

        df = pd.DataFrame(tmp)
        _key = self.m_tt_input_zhishu_name.text()
        df.to_excel(f"{self._get_today_dir()}/{_key}.xlsx", index=False)
        

    # 搜索指数
    @pyqtSlot() 
    def on_m_tt_btn_search_zhishu_clicked(self):
        _key = self.m_tt_input_zhishu_name.text()
        if _key == '':
            self._print_txt('请正确输入文本')
            return

        funds = []
        # 当日是否搜索过
        fname = self._get_today_dir() + "/" + f"{_key}_all.xlsx"
        if check_file_is_exist(fname):
            self._print_txt('今日已经搜素过')
            f1 = pd.read_excel(fname, dtype=str)
            for index, row in f1.iterrows():
                funds.append({'_id':row["_id"], 'NAME':row["NAME"]})


            self._cb_search_fund_list(funds)
            return
        
        pp = {
            'key': _key,
            'out_dir': self._get_today_dir(),
        }
        worker = self.work_mgr.get_worker_search(pp)
        worker.signals.log.connect(self._print_txt)
        worker.signals.search_fund_list.connect(self._cb_search_fund_list)
        self.pool.start(worker)

        return 
    
    def _get_tt_fund_info(self, mode):

        _key = self.m_tt_input_zhishu_name.text()
        if _key == '':
            self._print_txt('请正确输入文本')
            return None

        tmp = []
        total = self.m_tt_funds.rowCount()
        for i in range(total):
            code = self.m_tt_funds.item(i, 1).text()
            name = self.m_tt_funds.item(i, 2).text()
            tmp.append({'CODE': code, 'NAME': name})
        
        if len(tmp) == 0:
            self._print_txt('无选择基金')
            return None
        #####
        pp = {
            'mode': mode,
            'key': _key,
            'out_dir': self._get_today_dir(),
            'cur_funds': tmp,
        }

        worker = self.work_mgr.get_worker_fund(pp)
        worker.signals.log.connect(self._print_txt)
        worker.signals.search_fund_item.connect(self._cb_search_one_fund_detail)
        self.pool.start(worker)
 
    # 搜索基本信息
    @pyqtSlot()
    def on_m_tt_btn_search_detail_clicked(self):
        self._get_tt_fund_info(FUND_INFO_BASIC)
        
    # 搜索分红
    @pyqtSlot()
    def on_m_tt_btn_search_fenhong_clicked(self):
        self._get_tt_fund_info(FUND_INFO_FENHONG)
 
    # 搜索回撤
    @pyqtSlot()
    def on_m_tt_btn_search_drawdown_clicked(self):        
        self._get_tt_fund_info(FUND_INFO_DRAWDOWN)
 
    # 搜索管理费
    @pyqtSlot()
    def on_m_tt_btn_search_fee_clicked(self):        
        self._get_tt_fund_info(FUND_INFO_FEE)

    # 导出数据
    @pyqtSlot()
    def on_m_tt_btn_export_clicked(self):
        pp = self._get_tt_fund_info()
        if pp is None:
            return
        worker = self.work_mgr.get_worker_export(pp)
        worker.signals.log.connect(self._print_txt)
        worker.signals.search_fund_item.connect(self._cb_search_one_fund_detail)
        self.pool.start(worker)

    ### 债券
    @pyqtSlot()
    def on_m_tt_btn_bond_detail_clicked(self):
        params = {
            "mode": BOND_INFO_DETAIL,
        }
        worker = self.work_mgr.get_worker_bond(params=params)
        worker.signals.log.connect(self._print_txt)
        worker.signals.finished.connect(self._cb_search_bond_finished)
        self.pool.start(worker)
        self._print_txt("开始查询中...")

        
    @pyqtSlot()
    def on_m_tt_btn_bond_list_clicked(self):
        self._print_txt("开始查询中...")
        params = {
            "mode": BOND_INFO_LIST,
        }
        worker = self.work_mgr.get_worker_bond(params=params)
        worker.signals.log.connect(self._print_txt)
        worker.signals.finished.connect(self._cb_search_bond_finished)
        self.pool.start(worker)


    def _cb_search_one_fund_detail(self, fund:dict):
        # {'代码': '159660', '名称': '汇添富纳斯达克100ETF', '累计净值': '', '规模': '37.72', '基金经理': '过蓓蓓', '成立日': '2023-03-30', '管理人': '汇添富基金', '跟踪标的': '纳斯达克100指数', '年化跟踪误差': ' 1.05%', '交易状态': '场内交易  ', '购买手续费': '', '近1周': '-3.03%', '近1月': '-5.98%', '近3月': '-9.69%', '近6月': '-6.60%', '今年来': '-8.19%', '近1年': '13.80%', '近2年': '25.54%', '近3年': '--', '成立来': '77.74%', '2025': '17.24%', '2024': '26.68%', '2023': '--', '2022': '--', '2021': '--', '2020': '--', '2019': '--', '2018': '--'}
        # print(fund)   
        pass

    def _cb_search_fund_list(self, funds:list):
        self.cur_funds = funds

        self.m_tt_funds.setRowCount(0)

        for i,item in enumerate(funds):
            '''
            {'CODE': '019525', 
            'NAME': '华泰柏瑞纳斯达克100ETF发起式联接(QDII)C',
            'NEWTEXCH': '', 'STOCKMARKET': '', '_id': '019525'}'''

            cur = self.m_tt_funds.rowCount()

            self.m_tt_funds.insertRow(cur)
            self.m_tt_funds.setItem(cur, 0, QTableWidgetItem('X'))

            v2 = QTableWidgetItem(item['_id'])
            self.m_tt_funds.setItem(cur, 1, v2)

            v3 = QTableWidgetItem(item['NAME'])
            self.m_tt_funds.setItem(cur, 2, v3)

        self.m_tt_fund_info.setText(f"累计:{self.m_tt_funds.rowCount()}")


    def _cb_search_bond_finished(self):
        self._print_txt("搜索债券完成")
        pass

if __name__ == '__main__':
    # 创建应用程序和对象
    app = QApplication(sys.argv)
    window = Window()

    window.show()
    sys.exit(app.exec_())