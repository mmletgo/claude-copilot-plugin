"""
项目进度管理 MCP 工具 - 数据类型定义

使用 Pydantic 定义所有数据模型，确保类型安全和数据验证。
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class TaskStatusEnum(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class FunctionDef(BaseModel):
    """函数定义模型

    描述项目中需要实现的函数，包含签名、逻辑说明、依赖关系等。
    """
    id: str = Field(..., description="函数唯一标识符")
    name: str = Field(..., description="函数名称")
    file: str = Field(..., description="函数所在文件路径")
    test_file: Optional[str] = Field(None, description="对应的测试文件路径")
    signature: str = Field(..., description="函数签名")
    business_logic: str = Field(..., description="业务逻辑描述")
    code_logic: str = Field(..., description="代码实现逻辑描述")
    test_cases: list[str] = Field(default_factory=list, description="测试用例列表")
    dependencies: list[str] = Field(default_factory=list, description="依赖的函数ID列表")
    called_by: list[str] = Field(default_factory=list, description="被哪些函数调用")
    uses: list[str] = Field(default_factory=list, description="使用的外部库或模块")


class TaskStatus(BaseModel):
    """任务状态模型

    跟踪单个任务（函数）的实现状态。
    """
    id: str = Field(..., description="对应的函数ID")
    status: TaskStatusEnum = Field(TaskStatusEnum.PENDING, description="任务状态")
    notes: Optional[str] = Field("", description="任务备注")
    updated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="最后更新时间 (ISO格式)"
    )


class ProjectProgress(BaseModel):
    """项目进度信息模型

    汇总项目的整体进度情况。
    """
    project_name: str = Field("", description="项目名称")
    total: int = Field(0, description="总任务数")
    completed: int = Field(0, description="已完成任务数")
    in_progress: int = Field(0, description="进行中任务数")
    pending: int = Field(0, description="待处理任务数")
    blocked: int = Field(0, description="阻塞任务数")
    current_task: Optional[str] = Field(None, description="当前正在执行的任务ID")


class Architecture(BaseModel):
    """架构信息模型

    描述项目的整体架构设计。
    使用 Any 类型以支持灵活的 JSON 结构。
    """
    project_name: str = Field("", description="项目名称")
    created: str = Field("", description="创建日期")
    overview: str = Field("", description="项目概述")
    technical_stack: Any = Field(
        default_factory=dict,
        description="技术栈（可以是字典、列表等任意结构）"
    )
    project_structure: Any = Field(
        default_factory=dict,
        description="项目结构（可以是字符串或字典）"
    )
    data_structures: Any = Field(
        default_factory=list,
        description="数据结构（可以是列表或字典）"
    )


class ChangeLogEntry(BaseModel):
    """变更日志条目模型

    记录项目的变更历史。
    支持两种格式：带 function_id 的详细格式和简单的 date/description 格式。
    """
    date: Optional[str] = Field(None, description="变更日期")
    timestamp: Optional[str] = Field(None, description="变更时间 (ISO格式)")
    function_id: Optional[str] = Field(None, description="相关的函数ID")
    action: Optional[str] = Field(None, description="变更操作类型")
    description: str = Field("", description="变更描述")
    author: Optional[str] = Field(None, description="变更作者")


class ProgressData(BaseModel):
    """进度数据完整模型

    包含进度汇总和详细任务状态。
    """
    project_name: str = Field("", description="项目名称")
    summary: ProjectProgress = Field(default_factory=ProjectProgress, description="进度汇总")
    tasks: dict[str, TaskStatus] = Field(
        default_factory=dict,
        description="任务状态字典，键为函数ID"
    )
    changelog: list[ChangeLogEntry] = Field(
        default_factory=list,
        description="变更日志"
    )
