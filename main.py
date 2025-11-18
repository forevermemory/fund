
import sys
import time
from mainwindow import Ui_MainWindow

from PyQt5.Qt import *


from tools import tool
from tools import mythread
from tools import mylog
import threading
import os
from concurrent.futures import ThreadPoolExecutor





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
        self.m_tt_input_zhishu_name.setText('沪深300')

    def init_ui(self):
        self.setupUi(self)

        # 创建目录
        tool.check_dir("datas")
        # os.path.join(os.getcwd(), "images", 'xxx')
        tool.check_dir(self._get_today_dir())

        # 线程
        # 搜索指数列表
        self._MyThread_tt_do_search_zhishu_detail= mythread.MyThread_tt_do_search_zhishu_detail()
        self._MyThread_tt_do_search_zhishu_detail.on_out_text_signal.connect(self._print_txt)
        
        self._MyThread_tt_do_get_max_drawdown= mythread.MyThread_tt_do_get_max_drawdown()
        self._MyThread_tt_do_get_max_drawdown.on_out_text_signal.connect(self._print_txt)

    def _get_today_dir(self)->str:
        return "datas/"+tool.get_year_month_day()

    def _print_txt(self, s):
        self.m_log.append(s)

    ################### 信号

    def _th_do_search_zhishu(self, _key):
        tool.tt_do_search_zhishu(_key, self._get_today_dir())
        self._print_txt('搜索结束，共搜索到%d条结果' % 1)
        self._print_txt('如需要进一步获取详情，请点击获取详情按钮')
        self.m_tt_btn_search_zhishu.setEnabled(True)

    @pyqtSlot()
    def on_m_tt_btn_search_zhishu_clicked(self):
        self.m_tt_btn_search_zhishu.setEnabled(False)

        _key = self.m_tt_input_zhishu_name.text()
        if _key == '':
            self._print_txt('请正确输入文本')
            self.m_tt_btn_search_zhishu.setEnabled(True)
            return

        # 当日是否搜索过
        if tool.check_file_is_exist(self._get_today_dir() + "/" + f"{_key}.xlsx"):
            self._print_txt('今日已经搜素过')
            self.m_tt_btn_search_zhishu.setEnabled(True)
            return

        self._print_txt('正在搜索中....')
        # thread start
        self.executor.submit(self._th_do_search_zhishu, (_key,))
        # t = threading.Thread(target=self._th_do_search_zhishu, args=(_key,))
        # t.start()



    @pyqtSlot()
    def on_m_tt_btn_search_detail_clicked(self):
 
        _key = self.m_tt_input_zhishu_name.text()

        if _key == '':
            self._print_txt('请正确输入文本')
            return

        self._MyThread_tt_do_search_zhishu_detail.set_params(_key, self._get_today_dir())
        self._MyThread_tt_do_search_zhishu_detail.start()

    @pyqtSlot()
    def on_m_tt_btn_search_drawdown_clicked(self):
        print("=============")
 
        _key = self.m_tt_input_zhishu_name.text()

        if _key == '':
            self._print_txt('请正确输入文本')
            return

        self._MyThread_tt_do_get_max_drawdown.set_params(_key, self._get_today_dir())
        self._MyThread_tt_do_get_max_drawdown.start()

        print("============222=")

 




if __name__ == '__main__':
    # 创建应用程序和对象
    app = QApplication(sys.argv)
    window = Window()

    window.show()
    sys.exit(app.exec_())