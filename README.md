# Claude Copilot - AI 主驾开发模式

> **让 AI 成为主驾驶员，人类作为副驾监督者**

## 项目愿景

当前主流的 AI 辅助编程有两种模式：

| 模式 | 描述 | 问题 |
|------|------|------|
| **Vibe Coding** | 人类用自然语言描述需求，AI 一次性生成大量代码 | 代码质量难以保证，人类难以审查大量代码 |
| **AI 副驾** | 人类主导编码，AI 提供补全和建议 | 没有充分发挥 AI 的能力，效率提升有限 |

**Claude Copilot** 提出第三种模式：**AI 主驾 + 人类副驾**

```
┌─────────────────────────────────────────────────────────────┐
│                    AI 主驾开发模式                           │
├─────────────────────────────────────────────────────────────┤
│  AI (Claude)                    人类                        │
│  ├─ 理解需求                    ├─ 确认需求理解              │
│  ├─ 设计架构                    ├─ 审核架构设计              │
│  ├─ 拆分任务                    ├─ 调整任务优先级            │
│  ├─ 逐个实现函数                ├─ 确认实现思路              │
│  │   ├─ 解释业务逻辑            │   ├─ 补充业务细节          │
│  │   ├─ 解释代码逻辑            │   ├─ 提出修改建议          │
│  │   └─ 编写代码和测试          │   └─ 审核代码质量          │
│  └─ 更新文档和进度              └─ 最终验收                  │
└─────────────────────────────────────────────────────────────┘
```

### 核心理念

1. **AI 主导，人类监督**：AI 负责执行，人类负责决策和审核
2. **逐步确认，降低风险**：每个函数实现前都需要人类确认
3. **透明沟通，充分解释**：AI 解释业务逻辑和代码逻辑，确保人类理解
4. **持久记忆，跨会话协作**：通过文档和 MCP 工具保持项目状态

## 安装

### 方式一：通过插件市场安装（推荐）

```bash
# 1. 添加插件市场
/plugin marketplace add mmletgo/claude-copilot-plugin

# 2. 安装插件
/plugin install claude-copilot
```

### 方式二：手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/mmletgo/claude-copilot-plugin.git

# 2. 复制 commands 到 Claude Code
cp -r claude-copilot-plugin/plugins/claude-copilot/.claude/commands/* ~/.claude/commands/

# 3. 安装 MCP 服务器
pip install -r claude-copilot-plugin/plugins/claude-copilot/mcp/project-tracker/requirements.txt

# 4. 注册 MCP 服务器
claude mcp add --transport stdio project-tracker --scope user -- python /path/to/claude-copilot-plugin/plugins/claude-copilot/mcp/project-tracker/src/server.py
```

## 使用方法

### 第一步：项目规划 (`/plan`)

在项目根目录运行：

```bash
/plan
```

**工作流程：**

1. **需求澄清**：AI 复述需求，确认理解正确
2. **技术调研**：AI 查看现有代码，确定技术方案
3. **架构设计**：AI 设计完整架构，包括所有类和函数
4. **输出文档**：
   - `docs/prd.md` - 产品需求文档
   - `docs/architecture.json` - 架构设计（数据结构）
   - `docs/functions.json` - 函数定义（签名、逻辑、依赖）
   - `docs/progress.json` - 进度追踪

**示例对话：**

```
用户: /plan 实现一个用户认证模块

AI: 我的理解是：
- 需要实现用户注册、登录、登出功能
- 使用 JWT 进行身份验证
- 密码需要加密存储

我的理解对吗？有补充吗？

用户: 对的，还需要支持 OAuth 登录

AI: 好的，我会添加 OAuth 支持。技术方案如下：
- 使用 bcrypt 加密密码
- 使用 PyJWT 生成 token
- 使用 authlib 处理 OAuth

技术方案可以吗？

用户: 可以

AI: [输出架构设计和函数定义...]
架构设计可以吗？

用户: 可以

AI: [生成 docs/prd.md, docs/architecture.json, docs/functions.json, docs/progress.json]
```

### 第二步：逐个实现 (`/impl`)

在项目根目录运行：

```bash
/impl
```

**工作流程：**

1. **加载上下文**：通过 MCP 获取当前任务和依赖
2. **确认任务**：
   - 解释**业务逻辑**（为什么需要这个函数）
   - 解释**代码逻辑**（这个函数做什么）
3. **解释思路**：说明实现方案，等待确认
4. **编写代码**：确认后才开始编码
5. **编写测试**：实现对应的测试用例
6. **运行测试**：确保测试通过
7. **更新进度**：标记任务完成

**示例对话：**

```
用户: /impl

AI: 项目：用户认证模块
已完成：0 / 5
当前任务：hash_password

业务逻辑：
用户注册时需要安全存储密码，不能明文存储，所以需要这个哈希函数。

代码逻辑：
接收明文密码，使用 bcrypt 算法生成哈希值返回。

业务逻辑和代码逻辑我理解得对吗？有补充吗？

用户: 对的

AI: 实现思路：
1. 使用 bcrypt.gensalt() 生成随机盐值
2. 使用 bcrypt.hashpw() 生成哈希
3. 返回 UTF-8 编码的字符串

这个思路可以吗？需要调整吗？

用户: 可以

AI: [编写代码和测试，运行测试...]

实现完成，测试通过！
已完成：1 / 5，下一个：verify_password

实现和测试符合预期吗？需要修改吗？

用户: 符合预期，继续

AI: [继续下一个任务...]
```

### 修改业务逻辑

如果在实现过程中需要修改业务逻辑：

```
用户: 密码哈希应该使用 argon2 而不是 bcrypt

AI: 这个修改会影响业务逻辑，我需要更新相关文档。
确认修改内容：将密码哈希算法从 bcrypt 改为 argon2，对吗？

用户: 对

AI: [更新 docs/prd.md, docs/architecture.json, docs/functions.json]
[重新实现函数和测试]
```

## MCP 工具

插件包含一个 MCP 服务器，提供以下工具：

| 工具 | 描述 |
|------|------|
| `current_task_context` | 获取当前任务的完整上下文（项目状态、任务详情、依赖函数） |
| `architecture_overview` | 获取项目架构概述（技术栈、数据结构） |
| `task_status_update` | 更新任务状态 |
| `project_status` | 获取项目进度概览 |

## 文档格式

### architecture.json

```json
{
  "project_name": "项目名",
  "overview": "项目概述",
  "technical_stack": {
    "language": "Python 3.11+",
    "libraries": ["fastapi", "pydantic"]
  },
  "data_structures": [
    {
      "name": "User",
      "fields": [
        {"name": "id", "type": "int", "description": "用户ID"}
      ]
    }
  ]
}
```

### functions.json

```json
{
  "functions": [
    {
      "id": "F1",
      "name": "hash_password",
      "file": "auth/password.py",
      "signature": "def hash_password(password: str) -> str",
      "business_logic": "用户注册时需要安全存储密码",
      "code_logic": "使用 bcrypt 生成密码哈希",
      "test_cases": ["正常密码", "空密码", "特殊字符"],
      "dependencies": [],
      "called_by": ["F3"]
    }
  ]
}
```

### progress.json

```json
{
  "project_name": "项目名",
  "summary": {
    "total": 5,
    "completed": 2,
    "in_progress": 1,
    "pending": 2
  },
  "tasks": [
    {"id": "F1", "status": "completed", "notes": "测试通过"}
  ]
}
```

## 最佳实践

1. **先规划后实现**：始终先运行 `/plan`，确保架构设计完整
2. **保持专注**：每次 `/impl` 只实现一个函数
3. **及时反馈**：对 AI 的理解和实现方案提出修改建议
4. **定期审查**：查看生成的代码和文档，确保质量
5. **跨会话协作**：`clear` 后可以继续上次的进度

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
