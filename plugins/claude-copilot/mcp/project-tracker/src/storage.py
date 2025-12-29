"""
项目进度管理 MCP 工具 - JSON 文件读写

提供 JSON 文件的读写操作，管理架构、函数定义和进度数据。
"""

import json
from pathlib import Path
from typing import Any, Optional

from types_ import (
    Architecture,
    ChangeLogEntry,
    FunctionDef,
    ProgressData,
    ProjectProgress,
    TaskStatus,
    TaskStatusEnum,
)


class StorageError(Exception):
    """存储操作异常"""
    pass


def _get_docs_path(project_path: str) -> Path:
    """获取项目的 docs 目录路径"""
    return Path(project_path) / "docs"


def _get_architecture_path(project_path: str) -> Path:
    """获取 architecture.json 文件路径"""
    return _get_docs_path(project_path) / "architecture.json"


def _get_functions_path(project_path: str) -> Path:
    """获取 functions.json 文件路径"""
    return _get_docs_path(project_path) / "functions.json"


def _get_progress_path(project_path: str) -> Path:
    """获取 progress.json 文件路径"""
    return _get_docs_path(project_path) / "progress.json"


def _read_json_file(file_path: Path) -> dict[str, Any]:
    """读取 JSON 文件

    Args:
        file_path: JSON 文件路径

    Returns:
        解析后的 JSON 数据

    Raises:
        StorageError: 文件不存在或解析失败时抛出
    """
    if not file_path.exists():
        raise StorageError(f"文件不存在: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise StorageError(f"JSON 解析失败 ({file_path}): {e}")
    except IOError as e:
        raise StorageError(f"文件读取失败 ({file_path}): {e}")


def _write_json_file(file_path: Path, data: dict[str, Any]) -> None:
    """写入 JSON 文件

    Args:
        file_path: JSON 文件路径
        data: 要写入的数据

    Raises:
        StorageError: 写入失败时抛出
    """
    try:
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        raise StorageError(f"文件写入失败 ({file_path}): {e}")


def read_architecture(project_path: str) -> Architecture:
    """读取项目架构信息

    Args:
        project_path: 项目根目录路径

    Returns:
        Architecture 对象
    """
    file_path = _get_architecture_path(project_path)
    data = _read_json_file(file_path)
    return Architecture(**data)


def read_functions(project_path: str) -> list[FunctionDef]:
    """读取所有函数定义

    Args:
        project_path: 项目根目录路径

    Returns:
        FunctionDef 对象列表
    """
    file_path = _get_functions_path(project_path)
    data = _read_json_file(file_path)

    # 支持两种格式：直接数组或 {"functions": [...]} 对象
    if isinstance(data, list):
        functions_data = data
    elif isinstance(data, dict) and "functions" in data:
        functions_data = data["functions"]
    else:
        raise StorageError(f"无效的 functions.json 格式: {file_path}")

    return [FunctionDef(**func) for func in functions_data]


def read_progress(project_path: str) -> ProgressData:
    """读取项目进度信息

    Args:
        project_path: 项目根目录路径

    Returns:
        ProgressData 对象，包含汇总和任务详情
    """
    file_path = _get_progress_path(project_path)

    # 如果进度文件不存在，基于函数列表初始化
    if not file_path.exists():
        return _init_progress_from_functions(project_path)

    data = _read_json_file(file_path)

    # 获取项目名称（可能在根级别或 summary 里）
    project_name = data.get("project_name", "")

    # 解析 summary
    summary_data = data.get("summary", {})
    # 如果 summary 里没有 project_name，使用根级别的
    if "project_name" not in summary_data and project_name:
        summary_data["project_name"] = project_name
    summary = ProjectProgress(**summary_data)

    # 解析 tasks - 支持数组格式和字典格式
    tasks_raw = data.get("tasks", [])
    tasks: dict[str, TaskStatus] = {}

    if isinstance(tasks_raw, list):
        # 数组格式: [{"id": "F1", "status": "pending", ...}, ...]
        for task_info in tasks_raw:
            if isinstance(task_info, dict) and "id" in task_info:
                func_id = task_info["id"]
                tasks[func_id] = TaskStatus(**task_info)
    elif isinstance(tasks_raw, dict):
        # 字典格式: {"F1": {"id": "F1", "status": "pending", ...}, ...}
        for func_id, task_info in tasks_raw.items():
            if isinstance(task_info, dict):
                if "id" not in task_info:
                    task_info["id"] = func_id
                tasks[func_id] = TaskStatus(**task_info)

    # 解析 changelog - 支持 change_log 和 changelog 两种键名
    changelog_data = data.get("changelog", data.get("change_log", []))
    changelog = [ChangeLogEntry(**entry) for entry in changelog_data]

    return ProgressData(
        project_name=project_name,
        summary=summary,
        tasks=tasks,
        changelog=changelog
    )


def _init_progress_from_functions(project_path: str) -> ProgressData:
    """基于函数列表初始化进度数据

    Args:
        project_path: 项目根目录路径

    Returns:
        初始化的 ProgressData 对象
    """
    try:
        functions = read_functions(project_path)
    except StorageError:
        # 如果函数文件也不存在，返回空进度
        return ProgressData(
            summary=ProjectProgress(
                project_name="Unknown",
                total=0,
                pending=0
            ),
            tasks={},
            changelog=[]
        )

    # 初始化所有任务为 pending
    tasks: dict[str, TaskStatus] = {}
    for func in functions:
        tasks[func.id] = TaskStatus(
            id=func.id,
            status=TaskStatusEnum.PENDING
        )

    # 计算汇总
    total = len(functions)
    summary = ProjectProgress(
        project_name=Path(project_path).name,
        total=total,
        pending=total,
        completed=0,
        in_progress=0,
        blocked=0
    )

    return ProgressData(summary=summary, tasks=tasks, changelog=[])


def write_progress(project_path: str, progress_data: ProgressData) -> None:
    """写入项目进度信息

    Args:
        project_path: 项目根目录路径
        progress_data: ProgressData 对象
    """
    file_path = _get_progress_path(project_path)

    # 转换为可序列化的字典
    data = {
        "summary": progress_data.summary.model_dump(),
        "tasks": {
            func_id: task.model_dump()
            for func_id, task in progress_data.tasks.items()
        },
        "changelog": [entry.model_dump() for entry in progress_data.changelog]
    }

    _write_json_file(file_path, data)


def get_function_by_id(project_path: str, func_id: str) -> Optional[FunctionDef]:
    """根据 ID 获取单个函数定义

    Args:
        project_path: 项目根目录路径
        func_id: 函数 ID

    Returns:
        FunctionDef 对象，如果未找到返回 None
    """
    functions = read_functions(project_path)
    for func in functions:
        if func.id == func_id:
            return func
    return None


def get_functions_by_ids(project_path: str, func_ids: list[str]) -> list[FunctionDef]:
    """根据 ID 列表获取多个函数定义

    Args:
        project_path: 项目根目录路径
        func_ids: 函数 ID 列表

    Returns:
        FunctionDef 对象列表（保持请求顺序，跳过未找到的）
    """
    functions = read_functions(project_path)
    func_map = {func.id: func for func in functions}

    result: list[FunctionDef] = []
    for func_id in func_ids:
        if func_id in func_map:
            result.append(func_map[func_id])

    return result


def get_all_function_ids(project_path: str) -> list[str]:
    """获取所有函数 ID 列表

    Args:
        project_path: 项目根目录路径

    Returns:
        函数 ID 列表
    """
    functions = read_functions(project_path)
    return [func.id for func in functions]
