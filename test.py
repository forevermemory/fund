import requests
import re
import pandas as pd


# 041 长期纯债
# 042 短期纯债
# 043 混合债
# 044 定开
# 045 可转债
mapping = {
    "041": "长期纯债",
    "042": "短期纯债",
    "043": "混合债",
    "044": "定开债",
    "071": "定开债",
    "045": "可转债",
}

def repl_bond_fund_cate(m):
    return mapping[m.group(0)]

from openpyxl import load_workbook

def read_excel_skip_hidden(filename, sheet_name='Sheet1'):
    # 先用 openpyxl 打开
    wb = load_workbook(filename, data_only=True)
    ws = wb[sheet_name]

    # 找出隐藏的行号（注意 Excel 行号从 1 开始）
    hidden_rows = [
        row for row, dim in ws.row_dimensions.items()
        if dim.hidden
    ]

    # pandas 的 skiprows 从 0 开始，所以要 -1
    skip = [r - 1 for r in hidden_rows]

    # 正式读取
    return pd.read_excel(filename,dtype=str, sheet_name=sheet_name, skiprows=skip)


if __name__ == "__main__":
    from tools.tool import _tt_do_search_fund_item_fenhong

    _tt_do_search_fund_item_fenhong('563900')
    ##
    # from tools.tool import sql_session
    # df = pd.read_sql(f'select * from bond_fund where code in ("021928")', sql_session.connection())
    # print(df)