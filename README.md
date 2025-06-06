# Wind MCP (Model Context Protocol) Server

Wind MCP (Model Context Protocol) Server 是一个实现了 [Model Context Protocol](https://modelcontextprotocol.io/introduction) 标准的工具服务器。其核心功能是将 [WindPy](https://www.wind.com.cn/newsite/html/data_wds.html) 金融数据接口封装成可被大语言模型 (LLM) 和兼容 MCP 的应用（如 [FastMCP](https://gofastmcp.com/getting-started/welcome)）直接调用的标准化工具。

通过此项目，任何兼容 MCP 的客户端都能够跨平台（Linux, macOS, Windows）调用 WindPy API，解决了 WindPy 必须在 Windows GUI 环境下运行的限制。这使得在服务器端或 AI 应用中集成实时金融数据变得简单而高效。

## 主要功能

- **MCP 标准实现**：作为一个标准的 MCP 服务器，可以无缝对接到任何兼容的客户端或框架。
- **跨平台访问**：让 Linux 和 macOS 用户能够无缝调用 WindPy API。
- **稳定的后台服务**：通过 `pyro` 远程对象协议，将 WindPy API 封装为可在后台7x24小时运行的稳定服务。
- **简易的管理脚本**：提供 Shell 脚本，方便在 macOS/Linux 上部署和管理 Wind 服务。
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
│   ├── check_server_status.py # 检查远端服务状态的客户端
│   ├── gangtise_mcp_simple.py # 一个简单的客户端调用示例
│   └── wind_mcp_direct_server.py # 核心代理服务程序
└── tests/              # 测试用例
    ├── test_cn_indicators.py
    ├── test_date_functions.py
    ├── test_simple.py
    └── test_wind_client.py
```

## 安装与配置

**环境要求**:
- 服务端：一台安装了 Wind 金融终端的 Windows 电脑。
- 客户端：Python 3.x 环境，macOS, Linux 或 Windows。

**步骤**:

1.  **克隆项目**
    ```bash
    git clone https://github.com/abuttoncc/wind_mcp.git
    cd wind_mcp
    ```

2.  **创建并激活虚拟环境** (推荐)
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # 在 Windows 上使用 `venv\Scripts\activate`
    ```

3.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

## 如何使用

### 1. 在 Windows 服务端运行 Server

在安装了 Wind 终端的 Windows 电脑上，打开命令行，运行以下命令启动代理服务：

```bash
python src/wind_mcp_direct_server.py
```
服务默认会启动在 `0.0.0.0:8888`。请确保 Windows 防火墙允许该端口的入站连接。

### 2. 在客户端调用

在任何一台客户端机器上，您可以通过以下方式测试和调用。

- **检查服务状态**:
  修改 `src/check_server_status.py` 文件中的 `host` 变量为您的 Windows 服务器 IP 地址，然后运行：
  ```bash
  python src/check_server_status.py
  ```

- **运行示例**:
  同样，修改 `src/gangtise_mcp_simple.py` 文件中的服务器 IP，然后运行：
  ```bash
  python src/gangtise_mcp_simple.py
  ```
  该脚本会演示如何通过代理获取万科（000002.SZ）的日线数据。

### 3. (可选) 在 macOS 上作为服务运行

如果您希望在 macOS 上部署客户端或管理服务（例如，服务本身部署在 macOS 虚拟机中），可以使用提供的脚本。

1.  修改 `config/com.wind.mcpserver.plist` 文件，确保其中的路径指向您的项目路径。
2.  使用 `scripts/manage_wind_service.sh` 脚本来管理服务：
    ```bash
    # 加载并启动服务
    ./scripts/manage_wind_service.sh start

    # 停止并卸载服务
    ./scripts/manage_wind_service.sh stop

    # 查看服务状态
    ./scripts/manage_wind_service.sh status
    ```

## 作为 MCP (Model Context Protocol) 服务器

除了作为 WindPy 的远程代理，本项目本身就是一个完全遵循 [Model Context Protocol](https://modelcontextprotocol.io/introduction) 标准的 MCP 服务器。

这意味着任何兼容 MCP 的客户端（例如 [FastMCP](https://gofastmcp.com/getting-started/welcome) 框架或大语言模型应用）都可以直接将此服务添加为工具源，从而让语言模型具备调用 Wind 金融数据的能力。

### FastMCP 配置示例

您可以在您的 `FastMCP` 客户端配置文件中添加如下配置，来连接并使用本服务提供的工具：

```yaml
mcp_server:
  tools:
    - name: wind_data_service
      # 将 <your_windows_ip> 替换为运行服务端的主机IP地址
      url: http://<your_windows_ip>:8888/sse
      # 备注: 根据服务端启动的 --transport 参数，
      # URL 也可以是 /streamable_http
      description: "用于获取实时和历史金融数据的Wind工具集"
```

## 贡献代码

欢迎通过 Pull Request 的方式为本项目贡献代码。

## 许可证

本项目采用 [MIT](LICENSE) 许可证。 