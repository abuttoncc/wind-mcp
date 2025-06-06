#!/usr/bin/env python3
"""
Wind MCP 客户端测试脚本

用于测试 wind_mcp_direct_server.py 服务器是否正常工作
"""

import asyncio
import argparse
import json
# 修改导入，使用FastMCP的Client类
from fastmcp import Client


async def test_mcp_client(url, test_type="tools"):
    """
    测试MCP客户端与服务器的连接
    
    Args:
        url: 服务器URL
        test_type: 测试类型 (tools/test/wind)
    """
    print(f"连接到 {url} ...")
    
    try:
        # 使用FastMCP 2.6.0的Client类建立连接
        async with Client(url) as client:
            # 测试列出工具
            if test_type == "tools" or test_type == "all":
                print("\n获取可用工具列表...")
                tools = await client.list_tools()
                print(f"发现 {len(tools)} 个工具:")
                for i, tool in enumerate(tools, 1):
                    print(f"{i}. {tool.name}: {tool.description}")
            
            # 测试简单工具调用
            if test_type == "test" or test_type == "all":
                print("\n测试工具调用...")
                try:
                    result = await client.call_tool("test_tool")
                    print(f"测试工具返回: {result}")
                except Exception as e:
                    print(f"测试工具调用失败: {e}")
            
            # 测试Wind API
            if test_type == "wind" or test_type == "all":
                print("\n测试Wind API连接...")
                try:
                    # 调用wind_connection_status工具
                    status_result = await client.call_tool("wind_connection_status")
                    print(f"Wind连接状态: {status_result}")
                    
                    # 从TextContent中提取JSON数据
                    if status_result and len(status_result) > 0:
                        # 从第一个TextContent中提取文本
                        status_text = status_result[0].text
                        # 解析JSON
                        status_data = json.loads(status_text)
                        # 获取connected状态
                        is_connected = status_data.get("connected", False)
                        
                        if is_connected:
                            print("\n获取上证指数最新价格...")
                            result = await client.call_tool("wind_wsq", {
                                "codes": "000001.SH", 
                                "fields": "rt_last"
                            })
                            print(f"Wind API返回: {result}")
                except Exception as e:
                    print(f"Wind API调用失败: {e}")
            
            print("\n测试完成!")
    except Exception as e:
        print(f"连接服务器失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Wind MCP 客户端测试工具")
    parser.add_argument(
        "--url", 
        type=str, 
        default="http://localhost:8888/mcp/",
        help="服务器URL (默认: http://localhost:8888/mcp/)"
    )
    parser.add_argument(
        "--test", 
        type=str, 
        default="all", 
        choices=["tools", "test", "wind", "all"],
        help="测试类型: tools=列出工具, test=测试工具, wind=Wind API, all=全部"
    )
    
    args = parser.parse_args()
    
    # 运行测试客户端
    asyncio.run(test_mcp_client(args.url, args.test))


if __name__ == "__main__":
    main()