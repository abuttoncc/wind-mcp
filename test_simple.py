#!/usr/bin/env python3
"""
简单测试Wind MCP服务器基本功能
"""

import asyncio
import json
from fastmcp import Client


async def test_basic_function():
    """测试基本功能"""
    url = "http://localhost:8888/mcp/"
    
    print("连接到 {} ...".format(url))
    
    try:
        async with Client(url) as client:
            # 测试连接状态
            print("\n测试连接状态...")
            result = await client.call_tool("wind_connection_status")
            if result:
                print("连接状态: {}".format(result[0].text))
            
            # 测试获取指标映射
            print("\n测试获取指标映射...")
            result = await client.call_tool("get_common_indicators")
            if result:
                print("指标映射结果: {}".format(result[0].text[:100] + "..."))
            
            print("\n测试完成!")
    except Exception as e:
        print("测试失败: {}".format(e))


if __name__ == "__main__":
    asyncio.run(test_basic_function()) 