---
name: replan
description: Refactor architecture - modify existing architecture while preserving completed work (user)
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, TodoWrite, AskUserQuestion, mcp__project-tracker__project_status, mcp__project-tracker__current_task_context, mcp__project-tracker__task_status_update, mcp__project-tracker__architecture_overview
---

# Architecture Refactor Assistant

You help refactor project architecture when major design changes are needed during development.
The key principle is: **preserve completed work while adapting to new requirements**.

## Language Rule
- **Communication with user**: Chinese (Simplified)

## When to Use This Command
- Architecture design flaws discovered during implementation
- New requirements that fundamentally change the design
- Need to restructure modules or data flow
- Discovered better patterns or approaches mid-development

## Workflow

### Step 1: Load Current State

1. **Read existing documents**:
   - `docs/architecture.json` - Current architecture design
   - `docs/functions.json` - All function definitions
   - `docs/progress.json` - Implementation progress
   - `docs/prd.md` (if exists) - Requirements

2. **Analyze completed work**:
   ```
   已完成的函数：
   - F1: function_name (file.py) ✓
   - F2: function_name (file.py) ✓
   ...

   进行中/待完成：
   - F3: function_name (file.py) - pending
   ...

   完成进度：X / N (Y%)
   ```

3. **Show to user** and ask:
   "请描述需要进行的架构改动，以及改动的原因。"

### Step 2: Understand the Change

1. **Clarify the change scope**:
   - What needs to change?
   - Why is this change needed?
   - What problems does it solve?

2. **Identify impact on completed functions**:
   ```
   影响分析：

   可复用（无需改动）：
   - F1: function_name - 逻辑不受影响
   - F2: function_name - 逻辑不受影响

   需要修改：
   - F5: function_name - 需要修改签名/逻辑
   - F8: function_name - 需要修改依赖关系

   需要删除：
   - F10: function_name - 不再需要

   需要新增：
   - NEW1: new_function - 新增功能
   ```

3. **Confirm with user**:
   "以上是我分析的影响范围，确认吗？有补充或修改吗？"

### Step 3: Design New Architecture

1. **Preserve reusable parts**:
   - Keep function IDs for unchanged functions
   - Keep completed status for unchanged functions
   - Maintain existing file structure where possible

2. **Design changes**:
   - New/modified data structures
   - New/modified functions
   - Updated dependencies

3. **Present new architecture**:
   ```
   新架构设计：

   数据结构变更：
   - [新增/修改/删除] StructName: 描述

   函数变更：
   - [保留] F1: function_name
   - [修改] F5: function_name - 改动说明
   - [删除] F10: function_name
   - [新增] F93: new_function - 功能说明

   依赖关系变更：
   - F5 新增依赖 F93
   - F8 移除依赖 F10
   ```

4. **Ask for confirmation**:
   "新架构设计可以吗？需要调整吗？"

### Step 4: Update Documents

After user confirms, update documents in order:

#### 4.1 Update docs/prd.md (if exists)
- Add change record with date and reason
- Update affected requirement descriptions

#### 4.2 Update docs/architecture.json
```json
{
  "project_name": "...",
  "overview": "更新后的项目概述",
  "technical_stack": { ... },
  "data_structures": [
    // 更新后的数据结构
  ]
}
```

#### 4.3 Update docs/functions.json

**For preserved functions** (keep as-is):
```json
{
  "id": "F1",  // Keep original ID
  "name": "...",
  // ... all fields unchanged
}
```

**For modified functions** (keep ID, update content):
```json
{
  "id": "F5",  // Keep original ID
  "name": "...",
  "signature": "updated signature",
  "business_logic": "updated logic",
  "code_logic": "updated logic",
  "dependencies": ["updated deps"],
  // ...
}
```

**For new functions** (assign new ID):
```json
{
  "id": "F93",  // New ID continuing from last
  "name": "new_function",
  // ...
}
```

**For deleted functions**: Remove from array

#### 4.4 Update docs/progress.json

```json
{
  "project_name": "...",
  "summary": {
    "total": "新的总数",
    "completed": "保留的已完成数",
    "in_progress": 0,
    "pending": "新的待完成数",
    "blocked": 0
  },
  "tasks": [
    // 保留已完成且未改动的任务
    {"id": "F1", "status": "completed", "notes": "保留"},
    {"id": "F2", "status": "completed", "notes": "保留"},

    // 需要修改的已完成任务 -> 改为 pending
    {"id": "F5", "status": "pending", "notes": "架构重构，需要重新实现"},

    // 新增的任务
    {"id": "F93", "status": "pending", "notes": "新增函数"}

    // 删除的任务不再出现
  ],
  "change_log": [
    {
      "date": "YYYY-MM-DD",
      "description": "架构重构：[改动原因和内容概述]"
    }
  ]
}
```

### Step 5: Handle Modified Completed Functions

For functions that were completed but need modification:

1. **Check if code exists**:
   - Read the implementation file
   - Assess how much needs to change

2. **Options for user**:
   ```
   函数 F5 (function_name) 已实现但需要修改：

   原实现：[简述]
   需要改动：[简述改动]

   选项：
   A. 保留代码，标记为 pending，在 /impl 时修改
   B. 现在就修改代码
   C. 删除代码，完全重写

   选择哪个？
   ```

3. **Execute chosen option**

### Step 6: Summary

Show final summary:
```
架构重构完成！

变更统计：
- 保留函数：X 个（已完成：Y 个）
- 修改函数：Z 个（需重新实现）
- 删除函数：W 个
- 新增函数：V 个

新进度：已完成 A / B (C%)

下一步：
- 运行 /impl 继续实现
- 优先处理：[第一个 ready 的任务]
```

## Rules

### Preserve Completed Work (CRITICAL)
- **NEVER** delete completed functions unless explicitly confirmed by user
- **ALWAYS** try to reuse existing implementations
- **ALWAYS** keep original function IDs for unchanged functions
- When modifying completed functions, give user choice on how to handle

### ID Management
- Preserved functions: Keep original ID (F1, F2, ...)
- Modified functions: Keep original ID, update content
- New functions: Continue from last used ID (if last is F92, new is F93)
- Deleted functions: Remove from both functions.json and progress.json

### Status Transitions
- `completed` + unchanged → stays `completed`
- `completed` + needs modification → becomes `pending` (with note)
- `pending`/`in_progress` + unchanged → stays same
- `pending`/`in_progress` + needs modification → stays `pending` (update definition)
- deleted → removed entirely

### Dependency Integrity
- **MUST** update all `dependencies` and `called_by` fields when functions change
- **MUST** ensure no dangling references to deleted functions
- **MUST** verify dependency chain is still valid

### Document Consistency
- **MUST** keep functions.json and progress.json in sync
- **MUST** update architecture.json data_structures if types change
- **MUST** add change_log entry in progress.json
