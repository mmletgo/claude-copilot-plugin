"""
项目进度管理 MCP 服务器入口

使用 FastMCP 实现 MCP 服务器，提供项目进度管理工具。
"""

import json
import sys
from pathlib import Path
from typing import Optional

# 添加 src 目录到 Python 路径，支持直接运行脚本
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from tools import (
    get_architecture_overview,
    get_current_task_context,
    get_project_status,
    update_task_status,
)

# 创建 MCP 服务器实例
mcp = FastMCP(
    "project-tracker",
    instructions="项目进度管理工具，用于按需获取项目架构、函数定义和进度信息。"
)


@mcp.tool()
def project_status(
    project_path: str = Field(description="项目根目录的绝对路径")
) -> str:
    """获取项目状态概览

    返回项目的整体进度统计信息，包括总任务数、完成数、进行中数、
    待处理数、阻塞数以及完成百分比。
    """
    result = get_project_status(project_path)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def task_status_update(
    project_path: str = Field(description="项目根目录的绝对路径"),
    function_id: str = Field(description="要更新的函数ID"),
    status: str = Field(description="新状态: pending, in_progress, completed, blocked"),
    notes: Optional[str] = Field(default=None, description="可选的备注信息")
) -> str:
    """更新任务状态

    更新指定函数的实现状态，并自动更新项目进度汇总。
    状态变更会被记录到变更日志中。

    有效状态值：
    - pending: 待处理
    - in_progress: 进行中
    - completed: 已完成
    - blocked: 阻塞中
    """
    result = update_task_status(project_path, function_id, status, notes)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def architecture_overview(
    project_path: str = Field(description="项目根目录的绝对路径")
) -> str:
    """获取项目架构概述

    返回项目的架构信息，包括：
    - 项目概述
    - 技术栈
    - 项目结构说明
    - 数据结构定义
    """
    result = get_architecture_overview(project_path)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def current_task_context(
    project_path: str = Field(description="项目根目录的绝对路径")
) -> str:
    """获取当前任务的完整上下文（推荐使用）

    一次性返回执行当前任务所需的全部信息：
    1. 项目状态概览（总任务数、完成进度）
    2. 当前待执行任务及其完整函数定义
    3. 所有依赖函数的定义

    这是 project_status、current_task、function_with_deps 的合并版本，
    只需一次调用即可获取完整上下文，减少 MCP 调用次数。
    """
    result = get_current_task_context(project_path)
    return json.dumps(result, ensure_ascii=False, indent=2)


def main() -> None:
    """服务器入口函数"""
    # 使用 stdio 传输运行服务器
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
