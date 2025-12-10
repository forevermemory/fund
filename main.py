
import sys
import time
from mainwindow import Ui_MainWindow

from PyQt5.Qt import *
from PyQt5.QtGui import QIcon


from tools import tool
from tools import mythread
from tools import mylog
from tools import sql   
import threading
import os
import platform
import subprocess
import pandas as pd
from tools.param import Param



class Window(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("wwwww")

        self.items_code = {} # code -- 路径
        self.items_name = {} # name -- 路径
        self.items_name_code = {} # name -- code
        self.items_code_name = {} # code -- name

 
        self.init_ui()  # 界面绘制交给InitUi方法

        # tool.log_init(self.m_log)
        self.m_tt_input_zhishu_name.setText('纳斯达克')

        self._print_txt('晨星数据加载中')
        # sql.cx_data_init()
        self._print_txt('晨星数据加载完成')
        
        self._load_datas()

    def init_ui(self):
        self.setupUi(self)

        # 创建目录
        tool.check_dir("datas")
        # os.path.join(os.getcwd(), "images", 'xxx')
        tool.check_dir(self._get_today_dir())

        # 线程
        # 搜索指数列表
        self._mythread_s_list= mythread.MyThread_tt_do_search_zhishu_list()
        self._mythread_s_list.on_out_text_signal.connect(self._print_txt)
        
        self._mythread_s_detail= mythread.MyThread_tt_do_search_zhishu_detail()
        self._mythread_s_detail.on_out_text_signal.connect(self._print_txt)
        
        self._mythread_get_max_drawdown= mythread.MyThread_tt_do_get_max_drawdown()
        self._mythread_get_max_drawdown.on_out_text_signal.connect(self._print_txt)


        
        self._mythread_s_bondlist= mythread.MyThread_tt_do_get_bond_list()
        self._mythread_s_bondlist.on_out_text_signal.connect(self._print_txt)

        self._mythread_s_bond_detail= mythread.MyThread_tt_do_get_bond_detail_nh_hc()
        self._mythread_s_bond_detail.on_out_text_signal.connect(self._print_txt)

        self.m_tt_funds.cellClicked.connect(self._table_item_click)
        

    def _get_today_dir(self)->str:
        return "datas/"+tool.get_year_month_day()

    def _print_txt(self, s):
        self.m_log.append(s)

    def _table_item_click(self, row, col):
        self.m_log.append(f'{row}-{col}')
        if col == 0:
            self.m_tt_funds.removeRow(row)
        self.m_tt_fund_info.setText(f"累计:{self.m_tt_funds.rowCount()}")

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

        self.m_tt_ck_nianfei.setChecked(True)
        self.m_tt_ck_huiche.setChecked(True)
        self.m_tt_ck_fenhong.setChecked(True)



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

    def _th_do_search_zhishu(self, param):
        tool.tt_do_search_zhishu(param)
        self._print_txt('搜索结束，共搜索到%d条结果' % 1)
        self._print_txt('如需要进一步获取详情，请点击获取详情按钮')


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
        

    @pyqtSlot()
    def on_m_tt_btn_search_zhishu_clicked(self):

        _key = self.m_tt_input_zhishu_name.text()
        if _key == '':
            self._print_txt('请正确输入文本')
            return

        funds = []
        # 当日是否搜索过
        fname = self._get_today_dir() + "/" + f"{_key}_all.xlsx"
        if tool.check_file_is_exist(fname):
            self._print_txt('今日已经搜素过')
            f1 = pd.read_excel(fname, dtype=str)
            for index, row in f1.iterrows():
                funds.append({'_id':row["_id"], 'NAME':row["NAME"]})

        else:
            param = Param(_key, self._get_today_dir())
            self._print_txt('正在搜索中....')
            self._th_do_search_zhishu(param)

            # param = Param(_key, self._get_today_dir())
            # self._mythread_s_list.set_params(param)
            # self._mythread_s_list.start()

            funds = tool.tt_do_search_zhishu_cache()
        # # print(funds)

        # self.m_tt_funds.clear()
        self.m_tt_funds.setRowCount(0)

        for i,item in enumerate(funds):
            cur = self.m_tt_funds.rowCount()

            self.m_tt_funds.insertRow(cur)
            self.m_tt_funds.setItem(cur, 0, QTableWidgetItem('X'))

            v2 = QTableWidgetItem(item['_id'])
            self.m_tt_funds.setItem(cur, 1, v2)

            v3 = QTableWidgetItem(item['NAME'])
            self.m_tt_funds.setItem(cur, 2, v3)

        self.m_tt_fund_info.setText(f"累计:{self.m_tt_funds.rowCount()}")

    @pyqtSlot()
    def on_m_tt_btn_search_detail_clicked(self):
 
        _key = self.m_tt_input_zhishu_name.text()

        if _key == '':
            self._print_txt('请正确输入文本')
            return

        #####

        enable_nianfei = self.m_tt_ck_nianfei.isChecked()
        enable_fenhong = self.m_tt_ck_fenhong.isChecked()
        enable_huiche = self.m_tt_ck_huiche.isChecked()
        param = Param(_key, self._get_today_dir(), enable_nianfei, enable_fenhong, enable_huiche)
        self._mythread_s_detail.set_params(param)
        self._mythread_s_detail.start()

    @pyqtSlot()
    def on_m_tt_btn_search_drawdown_clicked(self):

        _key = self.m_tt_input_zhishu_name.text()

        if _key == '':
            self._print_txt('请正确输入文本')
            return

        self._mythread_get_max_drawdown.set_params(_key, self._get_today_dir())
        self._mythread_get_max_drawdown.start()


    @pyqtSlot()
    def on_m_info_bond_div_stock_clicked(self):
        self._print_txt('正在查询,请勿操作...')


        snq = tool._calc_cur_bond_div_stock_bond()
        self._print_txt(f'十年期国债收益率为:{snq}')
        avgv = tool._calc_cur_bond_div_stock_stock()
        self._print_txt(f'A股票的平均市盈为:{avgv}')
 
        v = 1/avgv*100/ snq
        self._print_txt(f'当前债股收益率比:{v}')
        
    @pyqtSlot()
    def on_m_tt_btn_search_bond_clicked(self):

        ft = self.m_tt_bond_tp.currentData()
        self._mythread_s_bondlist.set_params(self._get_today_dir(), ft)
        self._mythread_s_bondlist.start()
        
    @pyqtSlot()
    def on_m_tt_btn_search_bond2_clicked(self):
        
        self._mythread_s_bond_detail.set_params(self._get_today_dir())
        self._mythread_s_bond_detail.start()



if __name__ == '__main__':
    # 创建应用程序和对象
    app = QApplication(sys.argv)
    window = Window()

    window.show()
    sys.exit(app.exec_())