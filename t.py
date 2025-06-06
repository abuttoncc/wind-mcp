from WindPy import w

def query_hk_close(code="1810.HK", date="2025-05-31"):
    """
    查询指定港股在指定日期的收盘价
    :param code: 股票代码，如 '1810.HK'
    :param date: 查询日期，格式 'YYYY-MM-DD' 或 'YYYYMMDD'
    :return: WindPy 返回结果对象
    """
    # 启动Wind API
    w.start()
    if not w.isconnected():
        print("Wind API未连接，请检查Wind终端登录状态")
        return None

    # 查询收盘价
    result = w.wsd(code, "CLOSE", date, date)
    print("ErrorCode:", result.ErrorCode)
    print("Codes:", result.Codes)
    print("Fields:", result.Fields)
    print("Times:", result.Times)
    print("Data:", result.Data)
    return result

# 示例调用
if __name__ == "__main__":
    query_hk_close("1810.HK", "2025-05-12")