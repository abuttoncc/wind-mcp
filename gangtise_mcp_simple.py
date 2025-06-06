#!/usr/bin/env python
"""
简化版冈底斯MCP服务器
"""
import os
# 重要：在导入FastMCP之前设置端口
os.environ["FASTMCP_PORT"] = "8080"

import json
import requests
import time
import logging
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import socket
import asyncio

# 添加FastAPI需要的库 - 用于调试端点
try:
    from fastapi import FastAPI, Request, Response
    from fastapi.responses import JSONResponse, StreamingResponse
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    print("警告: 未安装FastAPI，将不启用额外的调试端点")

# 加载.env文件中的环境变量
load_dotenv()

# 冈底斯API配置
GANGTISE_ACCESS_KEY = os.environ.get("GANGTISE_ACCESS_KEY", "")
GANGTISE_SECRET_KEY = os.environ.get("GANGTISE_SECRET_KEY", "")
GANGTISE_TOKEN_URL = "https://open.gangtise.com/application/auth/oauth/open/loginV2"
GANGTISE_AGENT_URL = "https://open.gangtise.com/application/open-ai/ai/chat/sse"

# 创建日志目录
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("gangtise_mcp")

# 添加文件处理器
file_handler = logging.FileHandler(os.path.join(log_dir, "gangtise_mcp.log"))
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# 全局缓存
_token_cache = {
    "accessToken": None,
    "expiresAt": 0
}

def get_gangtise_token():
    """获取冈底斯API访问令牌"""
    now = int(time.time())
    # 缓存有效且未过期（预留60秒提前刷新）
    if _token_cache["accessToken"] and _token_cache["expiresAt"] - 60 > now:
        logger.info("使用缓存的token")
        return _token_cache["accessToken"]

    if not GANGTISE_ACCESS_KEY or not GANGTISE_SECRET_KEY:
        raise ValueError("GANGTISE_ACCESS_KEY 或 GANGTISE_SECRET_KEY 未配置")
    
    data = {
        "accessKey": GANGTISE_ACCESS_KEY,
        "secretAccessKey": GANGTISE_SECRET_KEY
    }
    
    try:
        logger.info(f"请求新token: {GANGTISE_TOKEN_URL}")
        resp = requests.post(GANGTISE_TOKEN_URL, json=data, timeout=10)
        
        if resp.status_code != 200:
            raise ValueError(f"获取accessToken失败: HTTP {resp.status_code}")
            
        resp_json = resp.json()
        if resp_json.get("code") != "000000":
            raise ValueError(f"获取accessToken失败: {resp_json.get('msg')}")
            
        token = resp_json["data"]["accessToken"]
        expires_in = resp_json["data"].get("expiresIn", 3600)  # 单位秒，默认1小时
        _token_cache["accessToken"] = token
        _token_cache["expiresAt"] = now + int(expires_in)
        logger.info("成功获取新token")
        return token
    except Exception as e:
        logger.error(f"获取accessToken异常: {str(e)}")
        raise

# 初始化MCP服务
mcp = FastMCP("GangtiseAgent")

# 直接暴露关键工具函数方便测试
@mcp.tool()
async def mcp_diagnostics() -> Dict[str, Any]:
    """
    诊断MCP服务状态，获取系统信息和已注册工具
    
    Returns:
        包含诊断信息的字典
    """
    logger.info("="*80)
    logger.info("🔍 运行MCP服务诊断")
    logger.info("-"*80)
    
    # 获取所有注册的工具
    registered_tools = []
    try:
        tools = await mcp.list_tools()
        for tool in tools:
            registered_tools.append({
                "name": tool.name,
                "description": tool.description,
            })
            
        result = {
            "status": "healthy",
            "timestamp": time.time(),
            "hostname": socket.gethostname(),
            "registered_tools": registered_tools,
            "tools_count": len(registered_tools),
            "environment": {
                "port": os.environ.get("FASTMCP_PORT", "Not Set"),
                "transport": mcp.transport_type if hasattr(mcp, 'transport_type') else "unknown"
            }
        }
        
        logger.info(f"诊断结果: 注册工具数量: {len(registered_tools)}")
        logger.info(f"工具列表: {', '.join([t.get('name', '') for t in registered_tools])}")
        logger.info("="*80)
        
        return result
    except Exception as e:
        error_result = {
            "status": "error",
            "timestamp": time.time(),
            "error": str(e),
            "hostname": socket.gethostname()
        }
        logger.error(f"诊断失败: {str(e)}")
        logger.info("="*80)
        return error_result

# 添加测试工具 - 不使用协程包装，便于测试
@mcp.tool()
async def simple_echo(message: str) -> str:
    """
    简单回显测试工具
    
    Args:
        message: 要回显的消息
        
    Returns:
        原样返回输入的消息
    """
    return f"Echo: {message}"

@mcp.tool()
async def query_gangtise(query: str, iter: Optional[int] = 3) -> str:
    """
    向冈底斯Agent发送查询，获取专业知识回答
    
    Args:
        query: 用户提问文本
        iter: 思考轮次，默认3轮
        
    Returns:
        字符串形式的回答
    """
    # 添加明显的日志标记表示工具被调用
    logger.info("="*80)
    logger.info(f"🔍 冈底斯工具被调用! 查询: \"{query}\"")
    logger.info(f"查询参数: iter={iter}")
    logger.info("-"*80)
    
    try:
        # 获取访问令牌
        token = get_gangtise_token()
        
        # 请求头
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "Accept": "text/event-stream"  # 使用SSE格式
        }
        
        # 请求体
        request_data = {
            "text": query,
            "mode": "deep_research",  # 深度研究模式
            "askChatParam": {
                "iter": iter  # 思考轮次
            }
        }
        
        # 发送请求
        logger.info(f"发送请求到冈底斯API: {GANGTISE_AGENT_URL}")
        logger.info(f"请求数据: {json.dumps(request_data, ensure_ascii=False)}")
        
        start_time = time.time()
        with requests.post(
            GANGTISE_AGENT_URL,
            headers=headers,
            json=request_data,
            stream=True,  # 使用流式模式
            timeout=180   # 延长超时时间
        ) as response:
            if response.status_code != 200:
                error_msg = f"查询失败: HTTP {response.status_code}"
                logger.error(error_msg)
                return error_msg
            
            # 收集回答片段
            answer_fragments = []
            
            # 处理SSE流
            logger.info("开始接收SSE数据流...")
            for line in response.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data:"):
                    continue
                    
                data_text = line[5:].strip()
                if not data_text:
                    continue
                
                # 尝试解析JSON
                try:
                    if data_text.startswith("{"):
                        data_obj = json.loads(data_text)
                        
                        # 获取phase和delta
                        phase = data_obj.get("phase", "")
                        result = data_obj.get("result", {})
                        
                        if isinstance(result, dict) and phase == "answer":
                            delta = result.get("delta", "")
                            if delta:
                                answer_fragments.append(delta)
                                
                except json.JSONDecodeError:
                    # 如果不是有效JSON，尝试直接提取delta
                    if '"delta":' in data_text:
                        try:
                            import re
                            delta_matches = re.findall(r'"delta":"([^"]*)"', data_text)
                            if delta_matches:
                                delta_text = delta_matches[0]
                                if delta_text:
                                    answer_fragments.append(delta_text)
                        except Exception:
                            pass
        
        # 处理耗时
        elapsed_time = time.time() - start_time
        logger.info(f"请求完成，耗时: {elapsed_time:.2f}秒")
        
        # 合并回答片段
        if not answer_fragments:
            error_msg = "未能从冈底斯获取有效回答，请重试。"
            logger.warning(error_msg)
            return error_msg
            
        # 合并所有片段
        final_answer = "".join(answer_fragments)
        
        # 解码Unicode
        try:
            if '\\u' in final_answer:
                final_answer = final_answer.encode('utf-8').decode('unicode_escape')
        except Exception as e:
            logger.warning(f"Unicode解码失败: {str(e)}")
            
        # 限制内容长度
        MAX_CHARS = 25000
        if len(final_answer) > MAX_CHARS:
            logger.warning(f"回答过长({len(final_answer)}字符)，截断至{MAX_CHARS}字符")
            final_answer = final_answer[:MAX_CHARS] + "\n\n[注：回答过长，已截断]"
            
        # 显示回答摘要
        answer_summary = final_answer[:200].replace("\n", " ")
        logger.info(f"成功获取冈底斯回答 (长度: {len(final_answer)})")
        logger.info(f"回答摘要: {answer_summary}...")
        logger.info("="*80)
        
        return final_answer
        
    except Exception as e:
        error_msg = f"查询冈底斯异常: {str(e)}"
        logger.error(error_msg)
        logger.info("="*80)
        return f"查询过程中发生错误: {str(e)}"

# 添加第二个工具 - 使用名称与系统提示完全一致
@mcp.tool(name="gangtise_knowledge")  # 显式指定工具名称
async def gangtise_knowledge(query: str, detail_level: Optional[int] = 2) -> str:
    """
    查询冈底斯知识库，获取专业领域知识回答
    
    Args:
        query: 用户提问内容，应该是具体的专业知识问题
        detail_level: 详细程度，1-简略，2-标准，3-详细
        
    Returns:
        冈底斯知识库的专业回答
    """
    logger.info("="*80)
    logger.info(f"🔎 冈底斯知识库工具被调用! 查询: \"{query}\"")
    logger.info(f"参数: detail_level={detail_level}")
    
    # 记录每次调用，帮助调试
    with open(os.path.join(log_dir, "tool_calls.log"), "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - gangtise_knowledge - 查询: {query}, detail_level: {detail_level}\n")
    
    # 实际上调用的是同一个API，这里复用query_gangtise的逻辑
    try:
        iter_map = {1: 1, 2: 3, 3: 5}  # 将详细程度映射到轮次
        iter_value = iter_map.get(detail_level, 3)
        
        logger.info(f"将detail_level={detail_level}映射到iter={iter_value}")
        result = await query_gangtise(query, iter_value)
        return result
    except Exception as e:
        error_msg = f"冈底斯知识库查询失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

# 处理各种可能的工具名称变体，确保向后兼容
@mcp.tool(name="query_gangtise")  # 原始名称
async def query_gangtise_alias(query: str, iter: Optional[int] = 3) -> str:
    """
    向冈底斯Agent发送查询，获取专业知识回答（别名版本）
    
    Args:
        query: 用户提问文本
        iter: 思考轮次，默认3轮
        
    Returns:
        字符串形式的回答
    """
    logger.info("="*80)
    logger.info(f"💡 冈底斯工具被调用(别名版)! 查询: \"{query}\"")
    logger.info(f"查询参数: iter={iter}")
    
    # 记录每次调用，帮助调试
    with open(os.path.join(log_dir, "tool_calls.log"), "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - query_gangtise - 查询: {query}, iter: {iter}\n")
    
    # 调用原始查询功能
    return await query_gangtise(query, iter)

# 添加系统提示中常见的格式
@mcp.tool(name="gangtise_agent")  # 另一个常见名称
async def gangtise_agent(query: str, detail_level: Optional[int] = 2) -> str:
    """
    使用冈底斯智能代理获取专业知识回答
    
    Args:
        query: 用户提问内容
        detail_level: 回答详细程度，1-简略，2-标准，3-详细
        
    Returns:
        冈底斯智能代理的专业回答
    """
    logger.info("="*80)
    logger.info(f"🤖 冈底斯智能代理被调用! 查询: \"{query}\"")
    logger.info(f"参数: detail_level={detail_level}")
    
    # 记录每次调用，帮助调试
    with open(os.path.join(log_dir, "tool_calls.log"), "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - gangtise_agent - 查询: {query}, detail_level: {detail_level}\n")
    
    # 转发到正式工具实现
    return await gangtise_knowledge(query, detail_level)

def get_registered_tools():
    """同步获取已注册的工具列表"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tools = loop.run_until_complete(mcp.list_tools())
        result = []
        for tool in tools:
            result.append({
                "name": tool.name,
                "description": tool.description
            })
        loop.close()
        return result
    except Exception as e:
        logger.error(f"获取已注册工具列表失败: {str(e)}")
        return []

# 启动前检查
def pre_flight_check():
    """启动前检查"""
    logger.info("-"*80)
    logger.info("执行启动前检查...")
    
    # 检查工具注册 - 修复协程调用问题
    registered_tools = []
    # 使用同步方式获取工具列表
    import asyncio
    try:
        # 创建一个新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # 在事件循环中运行协程
        tools = loop.run_until_complete(mcp.list_tools())
        for tool in tools:
            registered_tools.append(f"{tool.name}")
        loop.close()
    except Exception as e:
        logger.error(f"获取工具列表失败: {str(e)}")
        registered_tools = ["获取工具列表失败"]
    
    logger.info(f"已注册 {len(registered_tools)} 个工具: {', '.join(registered_tools)}")
    
    # 测试冈底斯API凭证
    try:
        # 尝试获取令牌，验证凭证
        token = get_gangtise_token()
        if token:
            logger.info("✅ 冈底斯API凭证验证成功")
    except Exception as e:
        logger.error(f"❌ 冈底斯API凭证验证失败: {str(e)}")
        logger.warning("服务将启动，但工具调用可能失败")
    
    # 检查日志目录
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        logger.info(f"创建日志目录: {log_dir}")
        
    # 初始化工具调用日志
    tool_log_path = os.path.join(log_dir, "tool_calls.log")
    with open(tool_log_path, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 服务启动 - 已注册工具: {', '.join(registered_tools)}\n")
    
    logger.info("启动前检查完成")
    logger.info("-"*80)

def start_server(port=8080, transport="sse"):
    """启动MCP服务器"""
    logger.info(f"启动冈底斯MCP服务器 (端口: {port}, 传输方式: {transport})")
    
    # 设置端口 - 同时设置FASTMCP_PORT和UVICORN_PORT
    os.environ["FASTMCP_PORT"] = str(port)
    os.environ["UVICORN_PORT"] = str(port)
    
    # 在这里添加一个新的环境变量来控制uvicorn的端口
    os.environ["UVICORN_HTTP_PORT"] = str(port)
    
    # 处理传输方式格式
    # FastMCP支持的传输方式: streamable_http, sse, stdio
    valid_transports = {
        "streamable-http": "streamable_http",  # 带连字符的写法转换为下划线写法
        "streamable_http": "streamable_http",  # 已经是正确写法
        "sse": "sse",                          # SSE格式，保持不变
        "stdio": "stdio"                       # stdio格式，保持不变
    }
    
    # 检查并转换传输方式
    if transport in valid_transports:
        transport = valid_transports[transport]
    else:
        logger.warning(f"不支持的传输方式: {transport}，默认使用sse")
        transport = "sse"  # 默认使用sse格式
        
    logger.info(f"使用传输方式: {transport}")
    
    # 执行启动前检查
    pre_flight_check()
    
    # 输出调试信息 - 帮助排查FastMCP URL路径问题
    logger.info("-" * 40)
    logger.info("MCP服务调试信息:")
    logger.info(f"端口: {port}")
    logger.info(f"传输方式: {transport}")
    logger.info(f"FastMCP接口路径:")
    logger.info(f"- 如果是sse传输方式，应使用: http://localhost:{port}/sse")
    logger.info(f"- 如果是streamable_http传输方式，应使用: http://localhost:{port}/streamable_http")
    logger.info("-" * 40)
    
    # 使用同步方式获取注册的工具信息 - 复用pre_flight_check中已经获取的信息
    logger.info("已注册的工具将在服务启动后可用")
    logger.info("-" * 40)
    
    logger.info("正在启动服务，请在另一个终端使用curl测试以下接口:")
    logger.info(f"curl http://localhost:{port}/sse")
    logger.info(f"或访问 http://localhost:{port}/sse?method=mcp_diagnostics")
    logger.info("-" * 40)
    
    # 检查FastMCP版本，确定正确的run()方法参数
    import inspect
    run_params = inspect.signature(mcp.run).parameters
    logger.info(f"FastMCP.run 方法的参数: {list(run_params.keys())}")
    
    # 启动服务器
    try:
        # 根据API兼容性使用正确的参数
        # 基于inspect结果，只使用支持的参数
        supported_params = {}
        if 'transport' in run_params:
            supported_params['transport'] = transport
        if 'mount_path' in run_params:
            # 一些版本可能需要mount_path参数
            supported_params['mount_path'] = None  # 使用默认值
            
        # 记录我们要使用的参数
        logger.info(f"使用参数启动FastMCP: {supported_params}")
        
        # 使用解包方式调用，确保只传递支持的参数
        mcp.run(**supported_params)
    except Exception as e:
        logger.error(f"启动服务器失败: {str(e)}")
        logger.error(f"尝试使用最简参数重新启动...")
        
        # 尝试使用最简参数
        try:
            # 最简单的调用，不传任何参数
            mcp.run()
        except Exception as e2:
            logger.error(f"最简启动也失败: {str(e2)}")
            logger.error("尝试只使用transport参数...")
            try:
                # 只使用transport参数
                mcp.run(transport=transport)
            except Exception as e3:
                logger.error(f"使用transport参数也失败: {str(e3)}")
                logger.error("服务启动失败，请检查FastMCP版本和兼容性")

if __name__ == "__main__":
    # 获取命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='启动冈底斯MCP服务器')
    parser.add_argument('--port', type=int, default=8080, help='服务器端口')
    parser.add_argument('--transport', type=str, default="sse", 
                       choices=["streamable-http", "sse", "stdio"], 
                       help='传输方式')
    
    args = parser.parse_args()
    
    # 重要：如果命令行参数指定了不同的端口，更新环境变量
    if args.port != 8080:
        os.environ["FASTMCP_PORT"] = str(args.port)
        logger.info(f"更新端口为: {args.port}")
    
    # 启动服务器
    start_server(port=args.port, transport=args.transport) 