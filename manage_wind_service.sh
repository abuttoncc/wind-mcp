#!/bin/bash

# Wind MCP服务管理脚本
PLIST_FILE="com.wind.mcpserver.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$LAUNCH_AGENTS_DIR/$PLIST_FILE"
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 确保LaunchAgents目录存在
mkdir -p "$LAUNCH_AGENTS_DIR"

case "$1" in
    install)
        echo "安装Wind MCP服务..."
        # 复制plist文件到LaunchAgents目录
        cp "$CURRENT_DIR/$PLIST_FILE" "$PLIST_PATH"
        echo "服务配置已安装到: $PLIST_PATH"
        ;;
    load)
        echo "加载Wind MCP服务..."
        launchctl load "$PLIST_PATH"
        echo "服务已加载"
        ;;
    unload)
        echo "卸载Wind MCP服务..."
        launchctl unload "$PLIST_PATH"
        echo "服务已卸载"
        ;;
    start)
        echo "启动Wind MCP服务..."
        launchctl start com.wind.mcpserver
        echo "服务已启动"
        ;;
    stop)
        echo "停止Wind MCP服务..."
        launchctl stop com.wind.mcpserver
        echo "服务已停止"
        ;;
    status)
        echo "检查Wind MCP服务状态..."
        launchctl list | grep com.wind.mcpserver
        if [ $? -eq 0 ]; then
            echo "服务正在运行"
        else
            echo "服务未运行"
        fi
        ;;
    logs)
        echo "显示最新日志..."
        echo "标准输出日志:"
        tail -n 20 "$CURRENT_DIR/logs/wind_mcp_output.log"
        echo "错误日志:"
        tail -n 20 "$CURRENT_DIR/logs/wind_mcp_error.log"
        ;;
    *)
        echo "Wind MCP服务管理工具"
        echo "用法: $0 {install|load|unload|start|stop|status|logs}"
        echo ""
        echo "命令说明:"
        echo "  install - 安装服务配置"
        echo "  load    - 加载服务到launchd（重启后会自动启动）"
        echo "  unload  - 从launchd卸载服务"
        echo "  start   - 启动服务"
        echo "  stop    - 停止服务"
        echo "  status  - 查看服务状态"
        echo "  logs    - 查看服务日志"
        ;;
esac

exit 0 