#!/usr/bin/env python3
"""
Wind API MCP直连服务器

此服务器直接连接Wind API，提供HTTP和SSE接口，不需要额外的Socket服务器。
支持所有Wind API功能，包括wsd、wss、wsq等数据查询。
"""

import argparse
import inspect
import logging
import os
import socket
import time
from typing import Dict, Any, Optional, List
import threading
from datetime import datetime

# 第三方库导入
import pandas as pd
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
# 直接导入Wind API
from WindPy import w
# 导入FastMCP 2.0
from fastmcp import FastMCP

# Wind自动登录尝试状态
wind_auto_login_attempted = False

# 常用Wind指标参数映射字典
WIND_COMMON_INDICATORS = {
    # 行情指标
    "收盘价": "close",
    "涨跌幅": "pct_chg",
    "换手率": "turn",
    "每股收益EPS-基本": "eps_basic",
    "净资产收益率ROE-平均": "roe_avg",
    # 可根据需要添加更多指标
    "开盘价": "open",
    "最高价": "high",
    "最低价": "low",
    "成交量": "volume",
    "成交额": "amt",
    "总市值": "mkt_cap",
    "流通市值": "mkt_cap_float",
    "市盈率TTM": "pe_ttm",
    "市净率": "pb_lf",
    "股息率TTM": "dividendyield2",
    "振幅": "swing",
    "涨停价": "up_limit",
    "跌停价": "down_limit"
}

# Wind日期函数信息
WIND_DATE_FUNCTIONS = {
    "tdays": {
        "name": "获取区间内日期序列",
        "description": "获取指定时间区间内的日期序列",
        "usage": "w.tdays(beginTime, endTime, options)",
        "example": (
            "w.tdays('2023-01-01', '2023-12-31', "
            "'Days=Trading;TradingCalendar=SSE')"
        )
    },
    "tdaysoffset": {
        "name": "日期偏移函数",
        "description": "根据基准日期计算偏移后的日期",
        "usage": "w.tdaysOffset(offset, beginTime, options)",
        "example": "w.tdaysoffset(-20, '2023-01-01', 'Days=Trading')"
    },
    "tdayscount": {
        "name": "日期计数函数",
        "description": "计算指定区间内的日期数量",
        "usage": "w.tdayscount(beginTime, endTime, options)",
        "example": "w.tdayscount('2023-01-01', '2023-12-31', 'Days=Trading')"
    }
}

# Wind日期函数参数
WIND_DATE_PARAMS = {
    # tdays/tdaysoffset/tdayscount共用参数
    "Days": {
        "description": "日期类型",
        "options": {
            "Trading": "交易日",
            "Weekdays": "工作日",
            "Alldays": "日历日"
        },
        "default": "Trading"
    },
    # tdays/tdaysoffset共用参数
    "Period": {
        "description": "周期类型",
        "options": {
            "D": "天",
            "W": "周",
            "M": "月",
            "Q": "季度",
            "S": "半年",
            "Y": "年"
        },
        "default": "D"
    },
    # 所有日期函数共用参数
    "TradingCalendar": {
        "description": "交易所日历",
        "options": {
            "SSE": "上海证券交易所",
            "SZSE": "深圳证券交易所",
            "CFFE": "中金所",
            "TWSE": "台湾证券交易所",
            "DCE": "大商所",
            "NYSE": "纽约证券交易所",
            "CZCE": "郑商所",
            "COMEX": "纽约金属交易所",
            "SHFE": "上期所",
            "NYBOT": "纽约期货交易所",
            "HKEX": "香港交易所",
            "CME": "芝加哥商业交易所",
            "Nasdaq": "纳斯达克证券交易所",
            "NYMEX": "纽约商品交易所",
            "CBOT": "芝加哥商品交易所",
            "LME": "伦敦金属交易所",
            "IPE": "伦敦国际石油交易所"
        },
        "default": "SSE"
    }
}

# Wind日期宏表达式
WIND_DATE_MACROS = {
    # 相对日期表达式
    "relative_dates": {
        "description": "相对日期表达式，格式：[-]N[单位]",
        "examples": [
            "-5D (前推5个日历日)",
            "-10TD (前推10个交易日)",
            "-1M (前推1个月)",
            "-2Q (前推2个季度)",
            "-1Y (前推1年)"
        ],
        "units": {
            "TD": "交易日",
            "D": "日历日",
            "W": "周",
            "M": "月",
            "Q": "季度",
            "S": "半年",
            "Y": "年"
        }
    },
    # 特殊日期宏
    "special_macros": {
        "time_points": {
            "ED": "截止日期",
            "SD": "开始日期",
            "LQ1": "去年一季",
            "LQ2": "去年二季",
            "LQ3": "去年三季",
            "LYR": "去年年报",
            "RQ1": "今年一季",
            "RQ2": "今年二季",
            "RQ3": "今年三季",
            "MRQ": "最新一期",
            "RYF": "本年初",
            "RHYF": "下半年初",
            "RMF": "本月初",
            "RWF": "本周一",
            "LWE": "上周末",
            "LME": "上月末",
            "LHYE": "上半年末",
            "LYE": "上年末",
            "IPO": "上市首日"
        },
        "examples": [
            "ED-1Y (一年前)",
            "IPO (上市首日)",
            "RYF": "本年初",
            "LYE": "上年末"
        ]
    }
}

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("wind-mcp-server")

# 创建FastAPI应用
app = FastAPI(title="Wind API MCP Direct Server")

# 创建FastMCP服务器 - 修改服务器名称为wind_mcp
mcp = FastMCP("wind_mcp")

@mcp.resource("resource://windpy-doc")
def windpy_doc() -> str:
    """WindPy六大核心函数参数、返回、示例和日期宏说明"""
    with open("README_WindPy_MCP.md", "r", encoding="utf-8") as f:
        return f.read()

@mcp.prompt("prompt://windpy-example")
def windpy_example_prompt() -> str:
    """WindPy常用查询示例"""
    return "请参考README_WindPy_MCP.md中的示例部分。"

# 初始化Wind API连接
try:
    w.start()
    is_connected = w.isconnected()
    logger.info(f"Wind API 连接状态: {is_connected}")
    if not is_connected:
        logger.warning("Wind API 未连接成功，请确保Wind终端已登录")
except Exception as e:
    logger.error(f"Wind API 初始化失败: {e}")
    is_connected = False


# 辅助函数: 将Wind数据转换为DataFrame
def _to_dataframe(wind_data):
    """将Wind数据转换为DataFrame"""
    if not hasattr(wind_data, 'Data'):
        return None
        
    data = wind_data.Data
    codes = wind_data.Codes
    fields = wind_data.Fields
    times = wind_data.Times
    
    # 根据不同的数据结构创建DataFrame
    if len(fields) == 1 and len(codes) > 1:
        # 单指标多代码
        df = pd.DataFrame(data[0], index=times, columns=codes)
    elif len(fields) > 1 and len(codes) == 1:
        # 多指标单代码
        df = pd.DataFrame(data, index=fields, columns=times).T
    else:
        # 其他情况
        df = pd.DataFrame(data, index=fields, columns=times)
        
    return df


# 辅助函数：将中文指标名转换为Wind代码
def _convert_cn_indicators(indicators):
    """将中文指标名转换为Wind代码
    
    Args:
        indicators: 字符串或列表形式的指标名
        
    Returns:
        转换后的Wind代码字符串
    """
    if not indicators:
        return indicators
    
    # 如果是字符串，检查是否包含逗号分隔的多个指标
    if isinstance(indicators, str):
        if ',' in indicators:
            # 分割成列表处理
            indicator_list = [i.strip() for i in indicators.split(',')]
            converted = []
            
            for ind in indicator_list:
                if ind in WIND_COMMON_INDICATORS:
                    converted.append(WIND_COMMON_INDICATORS[ind])
                else:
                    # 如果找不到匹配，保留原始输入
                    converted.append(ind)
            
            # 合并回字符串
            return ','.join(converted)
        else:
            # 单个指标
            return WIND_COMMON_INDICATORS.get(indicators, indicators)
    
    # 如果是列表
    elif isinstance(indicators, (list, tuple)):
        return [WIND_COMMON_INDICATORS.get(ind, ind) for ind in indicators]
    
    # 其他情况返回原始输入
    return indicators


# 工具函数：兼容 str/list 输入
def _normalize_codes_fields(val):
    if isinstance(val, list):
        return ",".join(val)
    return val

@mcp.tool()
def get_today_date(fmt: str = "%Y%m%d") -> dict:
    """
    获取服务器当前日期

    参数:
        fmt (str): 日期格式，默认"%Y%m%d"
    返回:
        dict: {"today": "20240604"}
    示例:
        get_today_date()  # {"today": "20240604"}
        get_today_date("%Y-%m-%d")  # {"today": "2024-06-04"}
    """
    try:
        today = datetime.today().strftime(fmt)
        return {"today": today}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def search_windpy_doc(query: str) -> dict:
    """
    检索WindPy官方API文档（仅限本服务支持的六个函数），返回相关内容片段。

    参数:
        query (str): 检索关键词或自然语言问题
    返回:
        dict: 包含'match'字段，内容为相关文档片段

    示例:
        result = search_windpy_doc("w.wsd 参数")
    """
    try:
        with open("README_WindPy_MCP.md", "r", encoding="utf-8") as f:
            doc = f.read()
        # 简单全文分段检索，返回包含query的段落（上下文3段）
        lines = doc.splitlines()
        matches = []
        for i, line in enumerate(lines):
            if query.lower() in line.lower():
                start = max(0, i-2)
                end = min(len(lines), i+3)
                matches.append("\n".join(lines[start:end]))
        if matches:
            return {"match": "\n---\n".join(matches)}
        else:
            return {"match": "未找到相关内容。请尝试更换关键词。"}
    except Exception as e:
        return {"match": f"检索失败: {e}"}

@mcp.tool()
def wind_wsd(
    codes,
    fields,
    beginTime: str,
    endTime: str,
    options: str = ""
) -> dict:
    """
    获取日时间序列数据（WSD）

    参数:
        codes (str or list): 证券代码，支持单个字符串或字符串列表，如"600030.SH"或["600010.SH","000001.SZ"]
        fields (str or list): 指标列表,支持单指标或多指标，如"CLOSE,HIGH,LOW,OPEN"或["CLOSE","HIGH"]
        beginTime (str): 起始日期，如: "2016-01-01"、"20160101"、"-5D"
        endTime (str): 截止日期，如: "2016-01-05"、"20160105"、"-2D"
        options (str): 以分号分隔的可选参数，如"Period=W;Days=Trading"
    返回:
        dict: 包含ErrorCode, Data, Codes, Fields, Times等
    示例:
        wind_wsd(["600000.SH","000001.SZ"], ["CLOSE","OPEN"], "20240101", "20240131")
        wind_wsd("600000.SH", "CLOSE", "20240101", "20240131")
    """
    try:
        codes_ = _normalize_codes_fields(codes)
        fields_ = _normalize_codes_fields(fields)
        result = w.wsd(codes_, fields_, beginTime, endTime, options)
        return {
            'ErrorCode': result.ErrorCode,
            'Data': result.Data,
            'Codes': result.Codes,
            'Fields': result.Fields,
            'Times': result.Times
        }
    except Exception as e:
        return {'ErrorCode': -1, 'error': str(e)}

@mcp.tool()
def wind_wss(
    codes,
    fields,
    options: str = ""
) -> dict:
    """
    获取日截面数据（WSS）

    参数:
        codes (str or list): 证券代码，支持单个字符串或字符串列表
        fields (str or list): 指标列表，支持多指标
        options (str): 以分号分隔的可选参数
    返回:
        dict: 包含ErrorCode, Data, Codes, Fields, Times等
    示例:
        wind_wss(["600111.SH", "600340.SH"], ["sec_name","return_1w"], "tradeDate=20180611")
        wind_wss("600111.SH", "sec_name", "tradeDate=20180611")
    """
    try:
        codes_ = _normalize_codes_fields(codes)
        fields_ = _normalize_codes_fields(fields)
        result = w.wss(codes_, fields_, options)
        return {
            'ErrorCode': result.ErrorCode,
            'Data': result.Data,
            'Codes': result.Codes,
            'Fields': result.Fields,
            'Times': result.Times if hasattr(result, 'Times') else []
        }
    except Exception as e:
        return {'ErrorCode': -1, 'error': str(e)}

@mcp.tool()
def wind_wses(
    codes,
    fields,
    beginTime: str,
    endTime: str,
    options: str = ""
) -> dict:
    """
    获取板块日序列数据（WSES）

    参数:
        codes (str or list): 板块ID，支持单个字符串或字符串列表
        fields (str or list): 仅支持单指标
        beginTime (str): 起始日期
        endTime (str): 截止日期
        options (str): 以分号分隔的可选参数
    返回:
        dict: 包含ErrorCode, Data, Codes, Fields, Times等
    示例:
        wind_wses(["a001010200000000","a001010100000000"], "sec_close_avg", "2018-08-21", "2018-08-27", "")
        wind_wses("a001010200000000", "sec_close_avg", "2018-08-21", "2018-08-27", "")
    """
    try:
        codes_ = _normalize_codes_fields(codes)
        fields_ = _normalize_codes_fields(fields)
        result = w.wses(codes_, fields_, beginTime, endTime, options)
        return {
            'ErrorCode': result.ErrorCode,
            'Data': result.Data,
            'Codes': result.Codes,
            'Fields': result.Fields,
            'Times': result.Times
        }
    except Exception as e:
        return {'ErrorCode': -1, 'error': str(e)}

@mcp.tool()
def wind_tdays(
    beginTime: str,
    endTime: str,
    options: str = ""
) -> dict:
    """
    获取区间内日期序列（TDAYS）

    参数:
        beginTime (str): 起始日期
        endTime (str): 截止日期
        options (str): 以分号分隔的可选参数
    返回:
        dict: 包含ErrorCode, TradingDays（日期字符串列表）
    示例:
        wind_tdays("20240101", "20240131")
    """
    try:
        result = w.tdays(beginTime, endTime, options)
        trading_days = []
        if hasattr(result, 'Data') and result.Data:
            for day in result.Data[0]:
                if hasattr(day, 'strftime'):
                    trading_days.append(day.strftime('%Y%m%d'))
                else:
                    trading_days.append(str(day))
        return {
            'ErrorCode': result.ErrorCode,
            'TradingDays': trading_days
        }
    except Exception as e:
        return {'ErrorCode': -1, 'error': str(e)}

@mcp.tool()
def wind_tdaysoffset(
    offset: int,
    beginTime: str,
    options: str = ""
) -> dict:
    """
    获取偏移后的日期（TDAYSOFFSET）

    参数:
        offset (int): 偏移参数，>0后推，<0前推
        beginTime (str): 参照日期
        options (str): 以分号分隔的可选参数
    返回:
        dict: 包含ErrorCode, OffsetDate（字符串）
    示例:
        wind_tdaysoffset(-10, "20240101")
    """
    try:
        result = w.tdaysoffset(offset, beginTime, options)
        offset_date = None
        if hasattr(result, 'Data') and result.Data and result.Data[0]:
            day = result.Data[0][0]
            if hasattr(day, 'strftime'):
                offset_date = day.strftime('%Y%m%d')
            else:
                offset_date = str(day)
        return {
            'ErrorCode': result.ErrorCode,
            'OffsetDate': offset_date
        }
    except Exception as e:
        return {'ErrorCode': -1, 'error': str(e)}

@mcp.tool()
def wind_tdayscount(
    beginTime: str,
    endTime: str,
    options: str = ""
) -> dict:
    """
    获取区间内日期数量（TDAYSCOUNT）

    参数:
        beginTime (str): 起始日期
        endTime (str): 截止日期
        options (str): 以分号分隔的可选参数
    返回:
        dict: 包含ErrorCode, Count（区间内日期数量）
    示例:
        wind_tdayscount("20240101", "20240131")
    """
    try:
        result = w.tdayscount(beginTime, endTime, options)
        count = None
        if hasattr(result, 'Data') and result.Data and result.Data[0]:
            count = result.Data[0][0]
        return {
            'ErrorCode': result.ErrorCode,
            'Count': count
        }
    except Exception as e:
        return {'ErrorCode': -1, 'error': str(e)}


# API文档页面
@app.get("/docs")
async def docs():
    """提供服务器文档页面"""
    docs_html = """
    <html>
        <head>
            <title>Wind API MCP直连服务器</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 800px; 
                    margin: 0 auto; 
                    padding: 20px; 
                }
                h1 { color: #333; }
                h2 { color: #666; margin-top: 30px; }
                pre { 
                    background-color: #f5f5f5; 
                    padding: 10px; 
                    border-radius: 5px; 
                    overflow-x: auto; 
                }
                code { font-family: monospace; }
                .tool { 
                    margin-bottom: 15px; 
                    padding: 10px;
                    border-left: 3px solid #4CAF50; 
                    background-color: #f9f9f9;
                }
                .tool h3 { margin-top: 0; color: #4CAF50; }
            </style>
        </head>
        <body>
            <h1>Wind API MCP直连服务器</h1>
            <p>本服务器提供Wind API的MCP接口，支持以下功能：</p>
            
            <h2>基础工具</h2>
            <div class="tool">
                <h3>get_today_date</h3>
                <p>获取服务器当前日期</p>
            </div>
            <div class="tool">
                <h3>search_windpy_doc</h3>
                <p>检索WindPy官方API文档（仅限本服务支持的六个函数）</p>
            </div>
            
            <h2>Wind数据工具</h2>
            <div class="tool">
                <h3>wind_wsd</h3>
                <p>获取历史序列数据</p>
            </div>
            <div class="tool">
                <h3>wind_wss</h3>
                <p>获取截面数据</p>
            </div>
            <div class="tool">
                <h3>wind_wses</h3>
                <p>获取板块成分股</p>
            </div>
            <div class="tool">
                <h3>wind_tdays</h3>
                <p>获取交易日历</p>
            </div>
            <div class="tool">
                <h3>wind_tdaysoffset</h3>
                <p>获取偏移后的日期</p>
            </div>
            <div class="tool">
                <h3>wind_tdayscount</h3>
                <p>获取区间内日期数量</p>
            </div>
            
            <h2>接口地址</h2>
            <ul>
                <li>MCP接口: <code>/mcp/</code> (FastMCP 2.6默认路径)</li>
                <li>文档页面: <code>/docs</code></li>
                <li>健康检查: <code>/health</code></li>
            </ul>
            
            <h2>使用示例</h2>
            <p>使用Python MCP客户端连接：</p>
            <pre><code>
from fastmcp import Client

# 连接到FastMCP 2.6服务器
async with Client("http://localhost:8888/mcp/") as client:
    # 获取上证指数最新价格
    result = await client.call_tool("wind_wsd", {
        "codes": "000001.SH", 
        "fields": "rt_last"
    })
    print(result)
    
    # 获取交易日历
    result = await client.call_tool("wind_tdays", {
        "start_date": "20230101",
        "end_date": "20230131"
    })
    print(result)
    
    # 使用数据集查询股票列表
    result = await client.call_tool("wind_wset", {
        "table_name": "sectorconstituent",
        "options": "date=20230601;sectorId=1000011263000000" # 上证50
    })
    print(result)
            </code></pre>
        </body>
    </html>
    """
    return StreamingResponse(
        iter([docs_html.encode()]), 
        media_type="text/html"
    )


# 添加健康检查接口
@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        connected = w.isconnected()
        tools = [
            "wind_wsd", "wind_wss", "wind_wses",
            "wind_tdays", "wind_tdaysoffset", "wind_tdayscount",
            "get_today_date", "search_windpy_doc"
        ]
        return JSONResponse({
            "status": "ok",
            "wind_connected": connected,
            "server_version": "1.0.0",
            "tools": tools
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "error": str(e)
        }, status_code=500)


def wind_keepalive(interval=60):
    """定时检测Wind API连接，断开时自动重连（避免死循环弹窗）"""
    global wind_auto_login_attempted
    while True:
        try:
            if not w.isconnected():
                if not wind_auto_login_attempted:
                    logger.warning("Wind API 断开，尝试自动重连...")
                    w.start()
                    wind_auto_login_attempted = True
                    if w.isconnected():
                        logger.info("Wind API 自动重连成功")
                        wind_auto_login_attempted = False
                    else:
                        logger.error("Wind API 自动重连失败，请手动登录Wind终端！")
                else:
                    logger.warning("Wind API 仍未连接，已尝试自动重连，等待人工干预...")
            else:
                wind_auto_login_attempted = False  # 恢复正常
        except Exception as e:
            logger.error(f"Wind API 自动重连异常: {e}")
        time.sleep(interval)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Wind API MCP直连服务器")
    parser.add_argument(
        "--host", 
        type=str, 
        default="127.0.0.1", 
        help="服务器主机地址"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="服务器端口"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="启用热重载"
    )
    
    args = parser.parse_args()
    
    # 检查Wind连接状态
    if not is_connected:
        logger.warning("Wind API未连接，某些功能可能不可用")
    
    logger.info(f"启动Wind API MCP直连服务器在 {args.host}:{args.port}")
    
    # 获取已注册的工具
    tool_funcs = [
        get_today_date, search_windpy_doc
    ]
    logger.info(f"已注册的工具: {', '.join(func.__name__ for func in tool_funcs)}")
    
    logger.info(f"访问文档: http://{args.host}:{args.port}/docs")
    
    # 显示FastMCP版本信息
    try:
        import fastmcp
        logger.info(f"FastMCP版本: {fastmcp.__version__}")
    except Exception as e:
        logger.error(f"获取FastMCP版本信息失败: {e}")
    
    # 检查FastMCP.run方法的参数
    try:
        # 添加服务器路径
        mcp_path = "/mcp"
        logger.info(f"FastMCP服务器路径: {mcp_path}")
        
        run_params = inspect.signature(mcp.run).parameters
        logger.info(f"FastMCP.run方法参数: {list(run_params.keys())}")
        
        # 启动FastMCP服务器
        logger.info("启动FastMCP服务器...")
        
        # 使用明确的HTTP传输和路径
        msg = (f"使用FastMCP 2.6运行，"
               f"请访问 http://{args.host}:{args.port}{mcp_path}")
        logger.info(msg)
        mcp.run(
            transport="streamable-http",
            host=args.host,
            port=args.port,
            path=mcp_path
        )
    except Exception as e:
        logger.error(f"FastMCP启动失败: {e}")
        logger.info("回退到uvicorn启动方式...")
        
        # 如果FastMCP服务器启动失败，回退到使用uvicorn启动FastAPI应用
        try:
            uvicorn.run(
                app, 
                host=args.host, 
                port=args.port, 
                reload=args.reload
            )
        except Exception as e2:
            logger.error(f"uvicorn启动也失败: {e2}")
            logger.error("服务器启动失败，请检查端口是否被占用或环境是否配置正确。")


if __name__ == "__main__":
    # 启动Wind API守护线程
    threading.Thread(target=wind_keepalive, daemon=True).start()
    main()