"""
项目进度管理 MCP 工具

用于优化 Claude Code 的 /impl 命令，按需获取项目信息。
"""

from .types import (
    Architecture,
    ChangeLogEntry,
    FunctionDef,
    ProgressData,
    ProjectProgress,
    TaskStatus,
    TaskStatusEnum,
)

__all__ = [
    "Architecture",
    "ChangeLogEntry",
    "FunctionDef",
    "ProgressData",
    "ProjectProgress",
    "TaskStatus",
    "TaskStatusEnum",
]


def main() -> None:
    """服务器入口函数（延迟导入以避免 mcp 依赖问题）"""
    from .server import main as server_main
    server_main()
