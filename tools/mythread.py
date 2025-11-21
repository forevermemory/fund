from PyQt5 import QtWidgets
from PyQt5.Qt import *

from tools.mylog import _my_log_set
from tools.tool import tt_do_search_zhishu_detail,tt_do_get_max_drawdown,tt_do_search_zhishu,tt_do_get_bond_list

class MyThread_tt_do_search_zhishu_list(QThread):
    on_out_text_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._key = ''
        self.out_dir = ''


    def set_params(self, _key, out_dir):
        self._key = _key
        self.out_dir = out_dir
        _my_log_set(self)

    def my_print(self,s:str):
        self.on_out_text_signal.emit(s)

    def run(self):
        self.my_print("处理开始")
        tt_do_search_zhishu(self._key, self.out_dir)
        self.my_print("处理完成")

class MyThread_tt_do_search_zhishu_detail(QThread):
    on_out_text_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._key = ''
        self.out_dir = ''


    def set_params(self, _key, out_dir):
        self._key = _key
        self.out_dir = out_dir
        _my_log_set(self)

    def my_print(self,s:str):
        self.on_out_text_signal.emit(s)

    def run(self):
        self.my_print("处理开始")
        tt_do_search_zhishu_detail(self._key, self.out_dir)
        self.my_print("处理完成")


class MyThread_tt_do_get_max_drawdown(QThread):
    on_out_text_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._key = ''
        self.out_dir = ''


    def set_params(self, _key, out_dir):
        self._key = _key
        self.out_dir = out_dir
        _my_log_set(self)

    def my_print(self,s:str):
        self.on_out_text_signal.emit(s)

    def run(self):
        self.my_print("处理回撤开始")
        tt_do_get_max_drawdown(self._key, self.out_dir)
        self.my_print("处理回撤完成")

class MyThread_tt_do_get_bond_list(QThread):
    on_out_text_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._key = ''
        self.out_dir = ''
        _my_log_set(self)


    def set_params(self, _key, out_dir):
        _my_log_set(self)

    def my_print(self,s:str):
        self.on_out_text_signal.emit(s)

    def run(self):
        self.my_print("处理债券基金开始")
        tt_do_get_bond_list(self.out_dir)
        self.my_print("处理债券基金完成")

