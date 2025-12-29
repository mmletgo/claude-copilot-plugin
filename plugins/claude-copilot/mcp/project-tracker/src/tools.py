"""
项目进度管理 MCP 工具 - 工具函数实现

提供 6 个核心工具函数，用于项目进度管理。
"""

from datetime import datetime
from typing import Any, Optional

from storage import (
    StorageError,
    get_function_by_id,
    get_functions_by_ids,
    read_architecture,
    read_functions,
    read_progress,
    write_progress,
)
from types_ import (
    ChangeLogEntry,
    FunctionDef,
    TaskStatus,
    TaskStatusEnum,
)


def _format_error(message: str) -> dict[str, Any]:
    """格式化错误响应"""
    return {
        "success": False,
        "error": message
    }


def _format_success(data: Any) -> dict[str, Any]:
    """格式化成功响应"""
    return {
        "success": True,
        "data": data
    }


def get_project_status(project_path: str) -> dict[str, Any]:
    """获取项目状态概览

    返回项目的整体进度统计信息。

    Args:
        project_path: 项目根目录路径

    Returns:
        包含项目状态概览的字典
    """
    try:
        progress = read_progress(project_path)
        summary = progress.summary

        # 计算完成百分比
        completion_rate = 0.0
        if summary.total > 0:
            completion_rate = round(summary.completed / summary.total * 100, 1)

        return _format_success({
            "project_name": summary.project_name,
            "total_tasks": summary.total,
            "completed": summary.completed,
            "in_progress": summary.in_progress,
            "pending": summary.pending,
            "blocked": summary.blocked,
            "completion_rate": f"{completion_rate}%",
            "current_task": summary.current_task
        })
    except StorageError as e:
        return _format_error(str(e))


def get_current_task(project_path: str) -> dict[str, Any]:
    """获取当前待执行任务

    返回第一个 in_progress 或 pending 状态的任务详情。
    优先返回 in_progress 的任务，如果没有则返回第一个 pending 任务。

    Args:
        project_path: 项目根目录路径

    Returns:
        包含当前任务详情的字典
    """
    try:
        progress = read_progress(project_path)
        functions = read_functions(project_path)

        # 建立函数 ID 到函数定义的映射
        func_map = {func.id: func for func in functions}

        # 优先查找 in_progress 的任务
        in_progress_task: Optional[TaskStatus] = None
        first_pending_task: Optional[TaskStatus] = None

        for func_id, task in progress.tasks.items():
            if task.status == TaskStatusEnum.IN_PROGRESS and in_progress_task is None:
                in_progress_task = task
                break
            elif task.status == TaskStatusEnum.PENDING and first_pending_task is None:
                first_pending_task = task

        # 确定当前任务
        current_task = in_progress_task or first_pending_task

        if current_task is None:
            return _format_success({
                "message": "所有任务已完成或没有待处理任务",
                "task": None
            })

        # 获取函数定义
        func_def = func_map.get(current_task.id)
        if func_def is None:
            return _format_error(f"找不到函数定义: {current_task.id}")

        return _format_success({
            "task_id": current_task.id,
            "status": current_task.status.value,
            "notes": current_task.notes,
            "function": {
                "name": func_def.name,
                "file": func_def.file,
                "signature": func_def.signature,
                "business_logic": func_def.business_logic,
                "code_logic": func_def.code_logic,
                "test_file": func_def.test_file,
                "test_cases": func_def.test_cases,
                "dependencies": func_def.dependencies,
                "uses": func_def.uses
            }
        })
    except StorageError as e:
        return _format_error(str(e))


def get_function_def(project_path: str, function_id: str) -> dict[str, Any]:
    """获取单个函数定义

    Args:
        project_path: 项目根目录路径
        function_id: 函数 ID

    Returns:
        包含函数定义的字典
    """
    try:
        func = get_function_by_id(project_path, function_id)

        if func is None:
            return _format_error(f"找不到函数: {function_id}")

        # 获取任务状态
        progress = read_progress(project_path)
        task_status = progress.tasks.get(function_id)

        return _format_success({
            "id": func.id,
            "name": func.name,
            "file": func.file,
            "test_file": func.test_file,
            "signature": func.signature,
            "business_logic": func.business_logic,
            "code_logic": func.code_logic,
            "test_cases": func.test_cases,
            "dependencies": func.dependencies,
            "called_by": func.called_by,
            "uses": func.uses,
            "status": task_status.status.value if task_status else "unknown",
            "notes": task_status.notes if task_status else None
        })
    except StorageError as e:
        return _format_error(str(e))


def get_function_with_deps(project_path: str, function_id: str) -> dict[str, Any]:
    """获取函数及其依赖的定义

    递归获取函数本身及其所有依赖的函数定义。

    Args:
        project_path: 项目根目录路径
        function_id: 函数 ID

    Returns:
        包含函数及其依赖定义的字典
    """
    try:
        # 获取主函数
        main_func = get_function_by_id(project_path, function_id)
        if main_func is None:
            return _format_error(f"找不到函数: {function_id}")

        # 收集所有依赖（包括递归依赖）
        all_dep_ids: set[str] = set()
        to_process: list[str] = list(main_func.dependencies)

        while to_process:
            dep_id = to_process.pop(0)
            if dep_id not in all_dep_ids:
                all_dep_ids.add(dep_id)
                dep_func = get_function_by_id(project_path, dep_id)
                if dep_func:
                    # 添加这个依赖的依赖
                    for nested_dep in dep_func.dependencies:
                        if nested_dep not in all_dep_ids:
                            to_process.append(nested_dep)

        # 获取所有依赖的函数定义
        dep_funcs = get_functions_by_ids(project_path, list(all_dep_ids))

        # 获取进度信息
        progress = read_progress(project_path)

        def func_to_dict(func: FunctionDef) -> dict[str, Any]:
            task_status = progress.tasks.get(func.id)
            return {
                "id": func.id,
                "name": func.name,
                "file": func.file,
                "signature": func.signature,
                "business_logic": func.business_logic,
                "code_logic": func.code_logic,
                "dependencies": func.dependencies,
                "uses": func.uses,
                "status": task_status.status.value if task_status else "unknown"
            }

        return _format_success({
            "main_function": func_to_dict(main_func),
            "dependencies": [func_to_dict(f) for f in dep_funcs],
            "total_dependencies": len(dep_funcs)
        })
    except StorageError as e:
        return _format_error(str(e))


def update_task_status(
    project_path: str,
    function_id: str,
    status: str,
    notes: Optional[str] = None
) -> dict[str, Any]:
    """更新任务状态

    Args:
        project_path: 项目根目录路径
        function_id: 函数 ID
        status: 新状态 (pending, in_progress, completed, blocked)
        notes: 可选的备注信息

    Returns:
        更新结果
    """
    try:
        # 验证状态值
        try:
            new_status = TaskStatusEnum(status)
        except ValueError:
            valid_statuses = [s.value for s in TaskStatusEnum]
            return _format_error(
                f"无效的状态: {status}。有效值: {', '.join(valid_statuses)}"
            )

        # 读取当前进度
        progress = read_progress(project_path)

        # 检查任务是否存在
        if function_id not in progress.tasks:
            # 如果任务不存在，尝试从函数列表创建
            func = get_function_by_id(project_path, function_id)
            if func is None:
                return _format_error(f"找不到函数: {function_id}")

            # 创建新任务状态
            progress.tasks[function_id] = TaskStatus(
                id=function_id,
                status=new_status,
                notes=notes,
                updated_at=datetime.now().isoformat()
            )
        else:
            # 更新现有任务
            old_status = progress.tasks[function_id].status
            progress.tasks[function_id].status = new_status
            progress.tasks[function_id].notes = notes
            progress.tasks[function_id].updated_at = datetime.now().isoformat()

            # 添加变更日志
            progress.changelog.append(ChangeLogEntry(
                function_id=function_id,
                action="status_change",
                description=f"状态从 {old_status.value} 变更为 {new_status.value}",
                timestamp=datetime.now().isoformat()
            ))

        # 重新计算汇总
        _recalculate_summary(progress)

        # 如果是 in_progress，更新当前任务
        if new_status == TaskStatusEnum.IN_PROGRESS:
            progress.summary.current_task = function_id
        elif progress.summary.current_task == function_id:
            progress.summary.current_task = None

        # 保存进度
        write_progress(project_path, progress)

        return _format_success({
            "function_id": function_id,
            "new_status": new_status.value,
            "notes": notes,
            "updated_at": progress.tasks[function_id].updated_at,
            "summary": {
                "total": progress.summary.total,
                "completed": progress.summary.completed,
                "in_progress": progress.summary.in_progress,
                "pending": progress.summary.pending,
                "blocked": progress.summary.blocked
            }
        })
    except StorageError as e:
        return _format_error(str(e))


def _recalculate_summary(progress: Any) -> None:
    """重新计算进度汇总

    Args:
        progress: ProgressData 对象（会被就地修改）
    """
    completed = 0
    in_progress = 0
    pending = 0
    blocked = 0

    for task in progress.tasks.values():
        if task.status == TaskStatusEnum.COMPLETED:
            completed += 1
        elif task.status == TaskStatusEnum.IN_PROGRESS:
            in_progress += 1
        elif task.status == TaskStatusEnum.PENDING:
            pending += 1
        elif task.status == TaskStatusEnum.BLOCKED:
            blocked += 1

    progress.summary.total = len(progress.tasks)
    progress.summary.completed = completed
    progress.summary.in_progress = in_progress
    progress.summary.pending = pending
    progress.summary.blocked = blocked


def get_architecture_overview(project_path: str) -> dict[str, Any]:
    """获取架构概述

    返回项目的架构信息，包括概述、技术栈、项目结构和数据结构。

    Args:
        project_path: 项目根目录路径

    Returns:
        包含架构信息的字典
    """
    try:
        arch = read_architecture(project_path)

        return _format_success({
            "project_name": arch.project_name,
            "overview": arch.overview,
            "technical_stack": arch.technical_stack,
            "project_structure": arch.project_structure,
            "data_structures": arch.data_structures
        })
    except StorageError as e:
        return _format_error(str(e))


def get_current_task_context(project_path: str) -> dict[str, Any]:
    """获取当前任务的完整上下文（合并工具）

    一次性返回：
    1. 项目状态概览
    2. 当前待执行的任务
    3. 当前任务的函数定义
    4. 依赖函数的定义

    这是 get_project_status、get_current_task、get_function_with_deps 的合并版本，
    用于减少 MCP 调用次数。

    Args:
        project_path: 项目根目录路径

    Returns:
        包含完整上下文的字典
    """
    try:
        # 1. 读取进度信息
        progress = read_progress(project_path)
        summary = progress.summary

        # 计算完成百分比
        completion_rate = 0.0
        if summary.total > 0:
            completion_rate = round(summary.completed / summary.total * 100, 1)

        # 2. 读取所有函数定义
        functions = read_functions(project_path)
        func_map = {func.id: func for func in functions}

        # 3. 查找当前任务
        # 优先返回 in_progress 任务
        # 其次返回第一个「依赖都已完成或无依赖」的 pending 任务
        in_progress_task: Optional[TaskStatus] = None
        ready_pending_task: Optional[TaskStatus] = None

        def is_task_ready(func_id: str) -> bool:
            """检查任务是否就绪（依赖都已完成或无依赖）"""
            func = func_map.get(func_id)
            if func is None:
                return False
            # 无依赖，直接就绪
            if not func.dependencies:
                return True
            # 检查所有依赖是否已完成
            for dep_id in func.dependencies:
                dep_task = progress.tasks.get(dep_id)
                if dep_task is None or dep_task.status != TaskStatusEnum.COMPLETED:
                    return False
            return True

        for func_id, task in progress.tasks.items():
            if task.status == TaskStatusEnum.IN_PROGRESS and in_progress_task is None:
                in_progress_task = task
                break
            elif task.status == TaskStatusEnum.PENDING and ready_pending_task is None:
                # 只选择依赖已完成的任务
                if is_task_ready(func_id):
                    ready_pending_task = task

        current_task = in_progress_task or ready_pending_task

        # 如果没有待处理任务
        if current_task is None:
            return _format_success({
                "project_status": {
                    "project_name": progress.project_name or summary.project_name,
                    "total_tasks": summary.total,
                    "completed": summary.completed,
                    "in_progress": summary.in_progress,
                    "pending": summary.pending,
                    "blocked": summary.blocked,
                    "completion_rate": f"{completion_rate}%"
                },
                "current_task": None,
                "message": "所有任务已完成或没有待处理任务"
            })

        # 4. 获取当前函数定义
        func_def = func_map.get(current_task.id)
        if func_def is None:
            return _format_error(f"找不到函数定义: {current_task.id}")

        # 5. 收集所有依赖（包括递归依赖）
        all_dep_ids: set[str] = set()
        to_process: list[str] = list(func_def.dependencies)

        while to_process:
            dep_id = to_process.pop(0)
            if dep_id not in all_dep_ids:
                all_dep_ids.add(dep_id)
                dep_func = func_map.get(dep_id)
                if dep_func:
                    for nested_dep in dep_func.dependencies:
                        if nested_dep not in all_dep_ids:
                            to_process.append(nested_dep)

        # 6. 构建依赖函数列表
        def func_to_dict(func: FunctionDef, include_full: bool = False) -> dict[str, Any]:
            task_status = progress.tasks.get(func.id)
            result: dict[str, Any] = {
                "id": func.id,
                "name": func.name,
                "file": func.file,
                "signature": func.signature,
                "status": task_status.status.value if task_status else "unknown"
            }
            if include_full:
                result.update({
                    "test_file": func.test_file,
                    "business_logic": func.business_logic,
                    "code_logic": func.code_logic,
                    "test_cases": func.test_cases,
                    "dependencies": func.dependencies,
                    "called_by": func.called_by,
                    "uses": func.uses
                })
            return result

        dep_funcs = [func_map[dep_id] for dep_id in all_dep_ids if dep_id in func_map]

        return _format_success({
            "project_status": {
                "project_name": progress.project_name or summary.project_name,
                "total_tasks": summary.total,
                "completed": summary.completed,
                "in_progress": summary.in_progress,
                "pending": summary.pending,
                "blocked": summary.blocked,
                "completion_rate": f"{completion_rate}%"
            },
            "current_task": {
                "task_id": current_task.id,
                "status": current_task.status.value,
                "notes": current_task.notes,
                "function": func_to_dict(func_def, include_full=True)
            },
            "dependencies": [func_to_dict(f, include_full=False) for f in dep_funcs],
            "total_dependencies": len(dep_funcs)
        })
    except StorageError as e:
        return _format_error(str(e))
