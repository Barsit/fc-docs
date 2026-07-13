# code-interpreter-v1 模板

code-interpreter-v1 模板提供安全隔离的代码执行沙箱环境，支持在云端安全地执行 Python、JavaScript 等语言代码，并提供文件管理、终端命令执行、上下文管理等完整的数据面 API。

code-interpreter-v1 模板对齐 E2B Code Interpreter 的代码上下文、代码执行、文件访问和命令能力。

## 功能特性

| **特性** | **说明** |
| --- | --- |
| 多语言代码执行 | 支持 Python、JavaScript 等语言代码的安全执行，保持执行上下文（变量跨调用保留） |
| 文件系统操作 | 完整的文件 CRUD 能力：上传、下载、读取、写入、创建目录、移动、删除，支持文本和二进制文件 |
| 终端命令执行 | 支持同步命令执行和交互式终端（PTY），支持颜色、光标控制、终端调整大小 |
| 上下文管理 | 独立的代码执行环境，支持创建多个上下文（Kernel），每个上下文保持独立的变量状态 |
| 进程管理 | 列出、查询、停止沙箱内运行的进程 |
| 安全隔离 | 基于函数实例独占隔离，每个沙箱实例拥有独立的文件系统和进程空间 |

## 适用场景

| **场景** | **说明** |
| --- | --- |
| AI Agent 代码沙箱 | 为 AI Agent 提供安全的代码执行环境，防止不可信代码访问或篡改宿主系统资源 |
| 数据分析 | 在沙箱中运行 Python 数据分析脚本，配合 pandas、numpy 等库处理数据 |
| 文件处理 | 上传文件到沙箱，执行格式转换、数据清洗等操作后下载结果 |
| 脚本执行与自动化 | 执行 Shell 命令、安装依赖、运行自动化脚本 |

## 默认配置

code-interpreter-v1 模板的默认配置如下：

| **配置项** | **默认值** | **说明** |
| --- | --- | --- |
| 容器镜像 | `code-interpreter-v1:v0.0.x` | 预置代码解释器沙箱镜像，版本由平台管理 |
| 默认端口 | 5000 | 沙箱服务监听端口 |
| CPU | 2 vCPU | 最低要求 |
| 内存 | 2048 MB | 最低要求 |
| 磁盘大小 | 10240 MB | 可选 512 MB 或 10240 MB |

## 架构说明

Code Interpreter API 分为控制面和数据面两个层面：

| **层面** | **说明** |
| --- | --- |
| 控制面 OpenAPI | 负责沙箱模板和沙箱实例资源的创建和生命周期管理 |
| 数据面 OpenAPI | 负责具体的代码执行、文件操作、终端命令、进程管理等功能调用 |

数据面 Base URL 格式：`https://{port}-{sandboxId}.{domain}/`（port 通常为 49999 或 49983，domain 为沙箱接入域名）

## SDK 使用方式

使用 code-interpreter-v1 模板时，是否需要显式指定 `template` 取决于 SDK：

| **SDK** | **template 参数** | **说明** |
| --- | --- | --- |
| `e2b_code_interpreter` SDK | 不需要指定 | 专用 SDK 默认创建 `code-interpreter-v1` 沙箱 |
| `e2b` SDK | 需要指定 `code-interpreter-v1` | 通用 SDK 默认创建 base 沙箱，需要显式选择 code-interpreter-v1 模板 |

**使用 `e2b_code_interpreter` SDK：**

```python
import os
from e2b_code_interpreter import Sandbox

sbx = Sandbox.create(
    api_key=os.environ["E2B_API_KEY"],
    api_url=os.environ["E2B_API_URL"],
    domain=os.environ["E2B_DOMAIN"],
)
execution = sbx.run_code("print('hello from code interpreter')")
print("".join(execution.logs.stdout))
sbx.kill()
```

TypeScript 示例：

```typescript
import { Sandbox } from "@e2b/code-interpreter";

const sbx = await Sandbox.create("code-interpreter-v1", {
  apiKey: process.env.E2B_API_KEY,
  apiUrl: process.env.E2B_API_URL,
  domain: process.env.E2B_DOMAIN,
});

try {
  const execution = await sbx.runCode("print('hello from code interpreter')");
  console.log(execution.logs.stdout.join(""));
} finally {
  await sbx.kill();
}
```

**使用 `e2b` SDK：**

```python
import os
from e2b import Sandbox

sbx = Sandbox.create(
    template="code-interpreter-v1",
    api_key=os.environ["E2B_API_KEY"],
    api_url=os.environ["E2B_API_URL"],
    domain=os.environ["E2B_DOMAIN"],
)
result = sbx.commands.run("python --version")
print(result.stdout)
sbx.kill()
```

## 使用流程

1. **选择 code-interpreter-v1 内置模板**：该模板为平台内置模板，无需自行构建，可直接创建沙箱实例。
2. **启动沙箱实例**：基于模板创建沙箱实例，获取沙箱 ID。
3. **执行代码**：通过 `run_code` 执行 Python 或 JavaScript 代码；如需隔离变量状态，可创建多个执行上下文。

## 核心 API 概览

数据面 API 的沙箱实例由请求 Host（`{port}-{sandboxId}.{domain}`）或 `X-Sandbox-Id` 请求头定位，因此以下路径均不再携带 `{sandboxId}` 路径段。控制面 API（创建、停止、删除、健康检查）通过控制面域名调用，路径携带 `{sandboxId}`。

### 沙箱实例管理

| **操作** | **方法** | **路径** |
| --- | --- | --- |
| 创建沙箱实例 | POST | `/sandboxes` |
| 获取沙箱详情 | GET | `/sandboxes/{sandboxId}` |
| 停止沙箱实例 | POST | `/sandboxes/{sandboxId}/pause` |
| 恢复沙箱实例 | POST | `/sandboxes/{sandboxId}/resume` |
| 删除沙箱实例 | DELETE | `/sandboxes/{sandboxId}` |
| 列出沙箱实例 | GET | `/sandboxes` |

创建沙箱实例请求示例：

```json
POST ${BASEURL}/sandboxes

{
  "templateID": "code-interpreter-v1"
}
```

响应示例：

```json
{
  "sandboxID": "sbx-01JCED8Z9Y6XQVK8M2NRST5WXY",
  "templateID": "code-interpreter-v1",
  "alias": "code-interpreter-v1",
  "envdVersion": "0.5.2",
  "startedAt": "2024-12-02T10:30:00Z",
  "endAt": "2024-12-02T10:45:00Z",
  "cpuCount": 2,
  "memoryMB": 2048,
  "diskSizeMB": 10240,
  "state": "running"
}
```

### 上下文管理

| **操作** | **方法** | **路径** |
| --- | --- | --- |
| 列出所有上下文 | GET | `/contexts` |
| 创建新上下文 | POST | `/contexts` |
| 获取上下文详情 | GET | `/contexts/{contextId}` |
| 删除上下文 | DELETE | `/contexts/{contextId}` |

创建上下文请求示例：

```json
POST ${BASEURL}/contexts

{
  "language": "python",
  "cwd": "/home/user"
}
```

### 代码执行

通过上下文同步执行代码：

```json
POST ${BASEURL}/contexts/execute

{
  "language": "python",
  "code": "print('hello from sandbox')",
  "timeout": 30
}
```

响应以 NDJSON（每行一个 JSON 对象）返回：

```json
{"type":"stdout","text":"hello from sandbox\n","timestamp":1783947280402990178}
{"type":"result","executionCount":1,"is_main_result":true}
{"type":"number_of_executions","execution_count":1}
```

### 文件系统操作

| **操作** | **方法** | **路径** |
| --- | --- | --- |
| 读取文件 | GET | `/files?path={path}` |
| 写入文件 | POST | `/files` |
| 列出目录 | POST | `/filesystem.Filesystem/ListDir` |
| 获取文件信息 | POST | `/filesystem.Filesystem/Stat` |
| 上传文件 | POST | `/files`（multipart/form-data，请求体上限 32 MiB） |
| 创建目录 | POST | `/filesystem.Filesystem/MakeDir` |
| 移动/重命名 | POST | `/filesystem.Filesystem/Move` |
| 删除文件/目录 | POST | `/filesystem.Filesystem/Remove` |

文本文件以 UTF-8 编码返回 `content` 字段，二进制文件以 base64 编码返回。上传文件使用 `multipart/form-data` 格式，请求体上限为 32 MiB，且包含 multipart 编码开销；超出时返回 `EntityTooLarge`。

### 终端与进程管理

| **操作** | **方法** | **路径** |
| --- | --- | --- |
| 启动进程 | POST | `/process.Process/Start` |
| 连接进程 | POST | `/process.Process/Connect` |
| 列出所有进程 | POST | `/process.Process/List` |
| 停止进程 | POST | `/process.Process/Kill` |
| 交互式终端（PTY） | POST | `/process.Process/Start`（带 `pty` 字段） |

终端与进程采用 Connect-RPC streaming 协议（`Content-Type: application/connect+json`），响应为 enveloped JSON 流。

启动进程请求示例（普通命令）：

```json
POST ${BASEURL}/process.Process/Start
Content-Type: application/connect+json

{"process":{"cmd":"/bin/bash","args":["-c","echo hello"],"envs":{},"cwd":"/home/user"},"stdin":false}
```

启动交互式终端（PTY）请求示例：

```json
{"process":{"cmd":"/bin/bash","args":["-i","-l"],"envs":{}},"pty":{"size":{"rows":24,"cols":80}}}
```

响应为 enveloped JSON 流，依次包含：

```json
{"event":{"start":{"pid":1}}}
{"event":{"data":{"pty":"<base64 编码的终端输出>"}}}
{"event":{"keepalive":{}}}
{"event":{"end":{"exitCode":0,"exited":true,"status":"exited"}}}
```

服务端每 30 秒向客户端发送一次 keepalive 事件，客户端可通过 `Keepalive-Ping-Interval` 请求头调整间隔（默认 30s，最大 60s）。终端输出为 base64 编码的 xterm 兼容数据（含 ANSI 转义序列）。

## 沙箱实例状态

沙箱实例在生命周期内经历以下状态：

| **状态** | **说明** |
| --- | --- |
| `running` | 就绪，可以使用 |
| `paused` | 已暂停（浅休眠），可恢复 |
| `terminated` | 已终止 |

## 使用限制

| **限制项** | **约束** |
| --- | --- |
| 沙箱生命周期 | 单个沙箱实例最长生命周期为 24 小时（`timeout` 参数上限 86400 秒） |
| 浅休眠超时 | 可通过 `sandboxIdleTimeoutSeconds` 参数设置 |
| 文件上传大小 | 单次上传请求体上限 32 MiB，包含 multipart 编码开销（超出返回 `EntityTooLarge`） |
| 代码执行超时 | 单次同步执行最大超时 30 秒 |

## 最佳实践

**及时清理资源**：完成任务后删除不需要的文件、上下文和沙箱实例，监控存储空间使用情况。

**合理配置超时时间**：短期任务使用较短的超时时间（5~10 分钟），长期任务适当延长（最长不超过 24 小时）。

**错误处理**：建议对 5xx 服务器错误实施指数退避重试，对 429 限流错误等待后重试。

## 相关文档

- [沙箱模板概述](../02.内置模板.md)
- [构建模板](../03.构建自定义镜像模板.md)
- [生命周期](../../01.沙箱/01.生命周期.md)
- [base 模板](base-模板.md)（仅需 envd 基础能力时选择）
- [browser 模板](browser-模板.md)（仅需浏览器自动化能力时选择）
- [All-In-One 模板](all-in-one-模板.md)（需要同时使用浏览器和代码执行能力时选择）
