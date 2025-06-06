#!/usr/bin/env python3
"""
测试Wind MCP服务器中文指标名称转换功能
"""

import asyncio
import json
from fastmcp import Client


async def test_indicators():
    """测试中文指标名称功能"""
    url = "http://localhost:8888/mcp/"
    
    print("连接到 {} ...".format(url))
    
    try:
        async with Client(url) as client:
            # 获取常用指标列表
            print("\n获取常用指标列表...")
            result = await client.call_tool("get_common_indicators")
            if result:
                # 从TextContent中提取JSON数据
                indicators_text = result[0].text
                # 解析JSON
                indicators_data = json.loads(indicators_text)
                # 获取指标列表
                indicators = indicators_data.get("indicators", {})
                
                print("找到 {} 个常用指标:".format(len(indicators)))
                for cn_name, code in indicators.items():
                    print("  {}: {}".format(cn_name, code))
            
            # 测试使用中文指标名称获取数据
            print("\n使用中文指标名称获取上证指数数据...")
            try:
                result = await client.call_tool("wind_wsq", {
                    "codes": "000001.SH", 
                    "fields": "收盘价,涨跌幅"
                })
                
                if result:
                    # 从TextContent中提取JSON数据
                    result_text = result[0].text
                    print("原始返回: {}".format(result_text))
                    # 解析JSON
                    result_data = json.loads(result_text)
                    
                    print("Wind API返回:")
                    print("  错误码: {}".format(result_data.get('ErrorCode')))
                    print("  代码: {}".format(result_data.get('Codes')))
                    print("  字段: {}".format(result_data.get('Fields')))
                    print("  时间: {}".format(result_data.get('Times')))
                    print("  数据: {}".format(result_data.get('Data')))
                else:
                    print("API调用返回空结果")
            except Exception as e:
                print("获取数据失败: {}".format(e))
            
            # 测试使用英文指标名称获取数据
            print("\n使用英文指标名称获取上证指数数据...")
            try:
                result = await client.call_tool("wind_wsq", {
                    "codes": "000001.SH", 
                    "fields": "close,pct_chg"
                })
                
                if result:
                    # 从TextContent中提取JSON数据
                    result_text = result[0].text
                    print("原始返回: {}".format(result_text))
                    # 解析JSON
                    result_data = json.loads(result_text)
                    
                    print("Wind API返回:")
                    print("  错误码: {}".format(result_data.get('ErrorCode')))
                    print("  代码: {}".format(result_data.get('Codes')))
                    print("  字段: {}".format(result_data.get('Fields')))
                    print("  时间: {}".format(result_data.get('Times')))
                    print("  数据: {}".format(result_data.get('Data')))
                else:
                    print("API调用返回空结果")
            except Exception as e:
                print("获取数据失败: {}".format(e))
            
            print("\n测试完成!")
    except Exception as e:
        print("测试失败: {}".format(e))


if __name__ == "__main__":
    asyncio.run(test_indicators()) 