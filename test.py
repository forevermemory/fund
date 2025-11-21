import requests


def get_cgb_10y_yield():
    """获取中国10年期国债收益率（东方财富）"""
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "secid": "0.00338",   # 10年国债收益率指数
        "fields": "f43"       # 收益率字段
    }
    r = requests.get(url, params=params).json()
    print(r)
    yield_val = r["data"]["f43"] / 10000    # 东方财富乘10000
    return yield_val * 100                  # 转为百分比


def get_index_pe_ratio():
    """获取沪深300 PE（东方财富指数行情）"""
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "secid": "1.000300",  # 沪深300指数
        "fields": "f162"      # 市盈率
    }
    r = requests.get(url, params=params).json()
    pe = r["data"]["f162"]
    return pe


def graham_index(bond_yield_percent, pe_ratio):
    equity_yield = 1 / pe_ratio * 100
    return bond_yield_percent / equity_yield


if __name__ == "__main__":
    bond_yield = get_cgb_10y_yield()
    pe = get_index_pe_ratio()

    print(f"10年期国债收益率: {bond_yield:.2f}%")
    print(f"沪深300 市盈率: {pe:.2f}")

    g = graham_index(bond_yield, pe)
    print(f"格雷厄姆指数: {g:.2f}")

    if g > 1:
        print("结论：股票相对偏贵")
    elif g < 1:
        print("结论：股票相对便宜")
    else:
        print("结论：股票估值大致合理")
