#!/usr/bin/env python3
"""
测试Wind MCP服务器日期函数信息获取功能
"""

import asyncio
import json
from fastmcp import Client


async def test_date_functions():
    """测试Wind日期函数信息获取功能"""
    url = "http://localhost:8888/mcp/"
    
    print("连接到 {} ...".format(url))
    
    try:
        async with Client(url) as client:
            # 获取所有日期函数信息
            print("\n获取所有日期函数信息...")
            result = await client.call_tool("get_date_functions")
            if result:
                # 从TextContent中提取JSON数据
                functions_text = result[0].text
                # 解析JSON
                functions_data = json.loads(functions_text)
                
                # 获取函数列表
                functions = functions_data.get("functions", {})
                print("找到 {} 个日期函数:".format(len(functions)))
                for func_name, func_info in functions.items():
                    print("  {}: {}".format(func_name, func_info.get("name")))
                
                # 获取参数列表
                params = functions_data.get("params", {})
                print("\n共有 {} 个参数:".format(len(params)))
                for param_name, param_info in params.items():
                    print("  {}: {}".format(param_name, param_info.get("description")))
                
                # 获取日期宏表达式
                macros = functions_data.get("date_macros", {})
                if "special_macros" in macros:
                    time_points = macros.get("special_macros", {}).get("time_points", {})
                    print("\n特殊日期宏表达式 ({} 个):".format(len(time_points)))
                    for macro, desc in list(time_points.items())[:5]:  # 只显示前5个
                        print("  {}: {}".format(macro, desc))
                    print("  ... 等")
            
            # 获取特定函数信息
            print("\n获取特定函数 (tdays) 信息...")
            result = await client.call_tool("get_date_functions", {
                "function_name": "tdays"
            })
            if result:
                # 从TextContent中提取JSON数据
                function_text = result[0].text
                # 解析JSON
                function_data = json.loads(function_text)
                
                # 获取函数信息
                function_info = function_data.get("function", {})
                print("函数名: {}".format(function_info.get("name")))
                print("描述: {}".format(function_info.get("description")))
                print("用法: {}".format(function_info.get("usage")))
                print("示例: {}".format(function_info.get("example")))
            
            print("\n测试完成!")
    except Exception as e:
        print("测试失败: {}".format(e))


if __name__ == "__main__":
    asyncio.run(test_date_functions()) 