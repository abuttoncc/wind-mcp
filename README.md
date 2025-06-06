# Wind MCP Server: 让大模型拥有 Wind API 的超能力

本项目是一个实现了 [Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP) 标准的工具服务器。

**其唯一目标是：将强大的 [WindPy](https://www.wind.com.cn/newsite/html/data_wds.html) 金融数据接口，封装成可被大语言模型 (LLM) 直接调用的标准化工具。**

通过本项目，任何安装了 Wind 金融终端的桌面客户端，都可以通过 MCP 的方式，让大模型（如 Cherry Studio, Cursor 内置的 AI）直接理解和操作 Wind API，查询实时金融数据、执行复杂的日期计算，就像一个专业的金融分析师。

## 可用工具 (Available Tools)

本服务器为大模型提供了以下即插即用的工具，使其能够与 Wind API 交互。

### 基础工具

| 工具名称 | 功能描述 |
| :--- | :--- |
| `get_today_date(fmt)` | 获取服务器当前日期，可指定格式。 |
| `search_windpy_doc(query)` | 在核心 WindPy 函数文档中进行关键词搜索，帮助模型理解API用法。 |

### Wind 数据工具

| 工具名称 | 功能描述 |
| :--- | :--- |
| `wind_wsd(...)` | **（核心）获取日时间序列数据。** 用于查询多个标的在一段时间内的历史日线行情、财务等数据。 |
| `wind_wss(...)` | **（核心）获取日截面数据。** 用于查询多个标的在特定日期的快照数据，如最新价、市盈率等。 |
| `wind_wses(...)` | 获取板块成分股在一段时间内的序列数据。 |
| `wind_tdays(...)` | 获取指定区间内的交易日历。 |
| `wind_tdaysoffset(...)` | 根据一个基准日期，计算向前或向后偏移指定交易日后的日期。 |
| `wind_tdayscount(...)` | 计算一个日期区间内包含的交易日数量。 |

---

## 设置与运行

### 1. 环境准备

确保您的 Windows 机器上已安装 **Wind金融终端** 并能正常登录。然后，安装 Python 依赖：

```bash
pip install -r requirements.txt
```

### 2. 启动服务

在项目根目录下，运行以下命令启动 MCP 服务器：

```bash
python src/wind_mcp_direct_server.py --host 0.0.0.0 --port 8888
```
*   `--host 0.0.0.0` 允许局域网内的其他设备访问。
*   `--port 8888` 您可以根据需要修改端口号。

### 3. 客户端配置

在任何兼容 MCP 标准的客户端（如 **Cherry Studio**, **Cursor** 等）中添加如下 JSON 配置，即可开始使用。

```json
{
  "mcpServers": {
    "wind_mcp": {
      "url": "http://localhost:<port>/mcp/",
      "transport": "streamable-http"
    }
  }
}
```
> **注意**: 请将 `<port>` 替换为实际运行服务器的 port 地址。


## 鸣谢 (Acknowledgements)

本项目基于以下优秀的开源项目构建，特此感谢：
-   **[FastMCP](https://github.com/GoFastMCP/fastmcp-py)**: 提供了轻量、高效的 Model Context Protocol 服务器实现。

## 主要功能

- **MCP 标准实现**：作为一个标准的 MCP 服务器，可以无缝对接到任何兼容的客户端或框架。
- **简易的管理脚本**：提供 Shell 脚本，方便在 macOS上部署和管理 Wind 服务。
- **清晰的项目结构**：代码、测试、文档和配置分离，易于理解和维护。

## 目录结构

项目已经为您重构为更清晰、更标准的结构：

```
.
├── .gitignore          # Git忽略文件配置
├── README.md           # 项目主说明文档
├── requirements.txt    # Python依赖库
├── config/             # 存放配置文件
│   └── com.wind.mcpserver.plist # (macOS) launchd服务配置示例
├── docs/               # 存放详细的补充文档
│   ├── README_WindPy_MCP.md
│   ├── 调用WindPy.md
│   └── 调用示例.md
├── logs/               # 存放日志文件 (此目录被.gitignore忽略)
├── scripts/            # 存放管理和工具脚本
│   └── manage_wind_service.sh # (macOS) 服务管理脚本
├── src/                # 核心源代码
│   └── wind_mcp_direct_server.py # 核心代理服务程序
└── tests/              # 测试用例
    ├── test_cn_indicators.py
    ├── test_date_functions.py
    ├── test_simple.py
    └── test_wind_client.py
```

本项目采用 [MIT](LICENSE) 许可证。 
