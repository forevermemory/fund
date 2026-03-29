import os
import json
from datetime import datetime
from threading import Lock

FUND_INFO_BASIC = 1
FUND_INFO_FEE = 2
FUND_INFO_DRAWDOWN = 3
FUND_INFO_FENHONG = 4

BOND_INFO_LIST = 1
BOND_INFO_DETAIL = 2

NETWORK_MODE_DHCP = 1
NETWORK_MODE_STATIC = 2

class state_manager():

    
    
    def __init__(self):
        
        # work_params = {
        #     "cmds": cmds,
        #     "version": "3.2.2",
        #     "ip": ip,
        #     "username": username,
        #     "password": password,
        #     "port": port,
        #     "serial": port,
        #     "net_option": net_option,
        #     "device_tree_option": device_tree_option,
        # }
        
        self.ssh_executor = None

        self.ssh_params = {}
        self.install_params = {}
        self.runing_status = "未开始"
        
        # 执行次数
        self.run_times = 0
        
        # 是否通过ssh连接测试
        self.ssh_connect_status = False
        
        # 下载软件安装脚本
        self.test_install_shell = False
        
        # 固态硬盘挂载和/data目录创建检查
        self.mount_ssd = False
        
        # 开发板信息
        self.test_board = False
        self.board_info = "未知"
        
        # 是否已经安装软件平台
        self.test_data = False
        self.data_status = "?"
        
        # 网络配置
        self.test_network = False
        
        
        self.install_software_cmd = ""
        self.install_software_doing = False
        self.install_software_progress = "0%"
        self.install_software_finished = False
        
        self.clean_cmd = ""
        self.clean_doing = False
        self.clean_finished = False
        
        self.device_tree_doing = False
        self.device_tree_header = ''
        self.device_tree_status = '?'
        
        self.device_tree_info = None
        

