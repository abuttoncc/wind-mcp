# Wind API MCP直连服务器

Wind API的MCP接口服务器，提供了一个直接连接Wind API的MCP服务，可通过HTTP或SSE方式调用。

## 功能特点

- 直接连接Wind API，不需要额外的Socket服务器
- 支持Wind API的主要功能(wsd, wss, wsq等)
- 提供标准MCP接口，可以与AI客户端无缝集成
- 支持多种传输方式(streamable_http, sse)
- 内置健康检查和诊断工具

## 安装依赖

1. 确保已安装Wind API并能正常使用
2. 安装Python依赖:

```bash
pip install -r requirements.txt
```

## 启动服务器

```bash
python wind_mcp_direct_server.py
```

可选参数:
- `--host`: 监听地址，默认为127.0.0.1
- `--port`: 监听端口，默认为8000
- `--transport`: 传输方式，可选streamable_http/sse/stdio，默认为sse
- `--reload`: 开发模式下启用热重载

例如:
```bash
python wind_mcp_direct_server.py --host 0.0.0.0 --port 8080 --transport streamable_http
```

## 使用方法

启动服务器后，可以通过以下方式访问:

1. MCP客户端接口: 
   - streamable-http: `http://localhost:8000/streamable_http`
   - sse: `http://localhost:8000/sse`

2. 文档页面: `http://localhost:8000/wind/docs`

3. 健康检查: `http://localhost:8000/wind/health`

### 示例代码

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# 使用MCP的标准URL
url = "http://localhost:8000/streamable_http"

async with streamablehttp_client(url) as (read, write):
    async with ClientSession(read, write) as session:
        # 获取上证指数最新价格
        result = await session.call_tool("wind_wsq", {
            "codes": "000001.SH", 
            "fields": "rt_last"
        })
        print(result)
```

## 可用工具

- `wind_wsq`: 获取实时行情数据
- `wind_wsd`: 获取历史序列数据
- `wind_wss`: 获取截面数据
- `wind_connection_status`: 检查Wind API连接状态
- `wind_start`: 重新启动Wind服务
- `mcp_diagnostics`: 查看服务诊断信息

## 故障排除

如果服务器无法启动或MCP客户端无法连接，请检查以下事项:

1. Wind API是否正常工作(使用普通Wind Python API测试)
2. 端口是否被占用(尝试更改端口)
3. 查看日志输出，检查错误信息
4. 使用`/wind/health`端点检查服务器状态
5. 尝试使用`mcp_diagnostics`工具检查MCP服务状态

对于服务器启动失败问题，可尝试不同的传输方式:
```bash
python wind_mcp_direct_server.py --transport sse
```
或
```bash
python wind_mcp_direct_server.py --transport streamable_http
```

## 注意事项

- 服务器默认只监听本地地址(127.0.0.1)，如需从其他机器访问，请使用`--host 0.0.0.0`
- Wind API需要在Windows环境下运行，并且需要有有效的Wind账号
- 部分高级功能(如订阅、回调等)暂未实现 