# all in one 模板

all in one 模板将 browser 模板与 code-interpreter-v1 模板能力合并，提供一个统一的云端隔离执行环境。all in one 沙箱既能做浏览器级自动化（CDP / VNC / 录制），也能做代码执行、文件管理与交互式终端，是 AI Agent 的"眼睛 + 大脑 + 手"。

all in one 模板对齐 E2B 中浏览器自动化与 Code Interpreter 协同使用的体验。

## 功能特性

| **特性** | **说明** |
| --- | --- |
| 浏览器自动化 | 集成 browser 模板能力，支持 CDP 协议、Puppeteer/Playwright 兼容、VNC 实时查看和操作录制 |
| 代码执行 | 集成 code-interpreter-v1 模板能力，支持 Python/JavaScript 代码执行、上下文管理、文件系统操作 |
| 终端命令 | 支持同步命令执行和 WebSocket 交互式终端（TTY） |
| 进程管理 | 列出、查询、停止沙箱内运行的进程 |
| 协同执行 | 在同一会话中同时使用浏览器和代码解释器，实现"浏览器抓取 → 代码处理"的端到端工作流 |
| 安全隔离 | 基于函数实例独占隔离，每个沙箱实例拥有独立的文件系统、浏览器实例和进程空间 |

## 适用场景

| **场景** | **说明** |
| --- | --- |
| AI Agent 复合任务 | 在同一会话中既能驱动浏览器完成页面交互，也能运行代码处理和分析数据 |
| 数据采集与处理 | 先用浏览器抓取动态页面，再在沙箱内运行脚本解析、清洗、导出结果 |
| 自动化测试 | 支持浏览器 E2E 与后台脚本协同执行，便于在受控容器环境中回放与问题定位 |
| 内容生成与归档 | 生成截图/PDF/录制，并把处理结果持久化或下载 |

## 默认配置

all in one 模板的默认配置如下：

| **配置项** | **默认值** | **说明** |
| --- | --- | --- |
| 容器镜像 | `sandbox-all-in-one:v0.9.30` | 预置一体化沙箱镜像 |
| 默认端口 | 5000 | 沙箱服务监听端口 |
| CPU | 4 vCPU | 默认规格，因需同时支撑浏览器和代码执行 |
| 内存 | 8192 MB（8 GB） | 默认规格 |
| 磁盘大小 | 10240 MB（10 GB） | 建议 10 GB 以存储浏览器数据和执行结果 |

> **说明**
>
> all in one 模板的默认 CPU 和内存规格高于 code-interpreter-v1 模板和 browser 模板，因为需要同时支撑浏览器运行时和代码执行环境。

## 与 browser 模板的区别

browser 模板提供浏览器运行时，默认通过 3000 端口暴露 CDP 和 VNC 能力，适合网页访问、页面交互、截图、数据采集和 UI 测试等浏览器自动化任务。它包含 E2B envd 兼容基础能力，但不提供 Code Interpreter 服务，因此不能通过 Code Interpreter 上下文直接执行 Python。

all in one 模板在浏览器能力之上叠加 Code Interpreter 服务，默认同时使用 3000 端口作为浏览器入口、5000 端口作为代码执行和文件管理入口。它可以在同一个沙箱会话中直接执行 Python，用于完成“浏览器抓取动态页面 → Python 解析/清洗/分析 → 文件导出”的复合流程。

| **对比项** | **browser 模板** | **all in one 模板** |
| --- | --- | --- |
| 核心定位 | 轻量浏览器自动化环境 | 浏览器自动化 + 代码执行的一体化环境 |
| 浏览器能力 | 支持 CDP、VNC、截图、页面交互 | 支持 CDP、VNC、截图、页面交互 |
| E2B envd 基础能力 | 支持 | 支持 |
| Code Interpreter 服务 | 不支持 | 支持 |
| 代码执行 | 不支持通过 Code Interpreter 执行 Python | 支持 Python / JavaScript 代码执行 |
| 文件处理 | 支持基础文件访问，不提供 Code Interpreter 文件 API | 支持文件 API、上下文内读写和处理 |
| 典型入口 | 3000（浏览器入口） | 3000（浏览器入口）/ 5000（代码入口） |
| 默认规格 | 2 vCPU / 2048 MB / 10240 MB 磁盘 | 4 vCPU / 8192 MB / 10240 MB 磁盘 |
| 推荐场景 | 只需要浏览器自动化 | 需要浏览器和代码执行协同 |

## 快速入门

### 第一步：准备 API Key

1. 登录 [函数计算控制台](https://fcnext.console.aliyun.com/)。
2. 参见[创建 API Key](../../../01.开始使用/02.创建%20API%20Key.md)创建并获取 API Key。
3. 通过 SDK 使用 API Key 与 API 端点创建沙箱（见下方示例）。

### 第二步：获取端点

all in one 沙箱提供以下端点：

| **端点** | **格式** | **用途** |
| --- | --- | --- |
| CDP 自动化端点 | `wss://{sbx.get_host(3000)}/ws/automation` | 浏览器自动化（Puppeteer/Playwright） |
| VNC 实时流端点 | `wss://{sbx.get_host(3000)}/ws/livestream` | 实时查看浏览器界面 |
| 数据面 REST API | `https://{accountID}.e2b-data.cn-hangzhou.aliyuncs.com/` | 代码执行、文件管理、终端命令 |

> **说明**：CDP 和 VNC 端点通过 SDK 的 `sbx.get_host(3000)` 获取 host 地址，连接时需要在请求头中携带 `X-Access-Token` 进行身份验证。

### 第三步：使用浏览器自动化

```javascript
const puppeteer = require('puppeteer-core');
const { Sandbox } = require('e2b');

const BROWSER_SANDBOX_PORT = 3000;

async function main() {
  const sbx = await Sandbox.create({ template: 'all-in-one-template', apiKey: E2B_API_KEY, timeout: 600 });
  try {
    const host = sbx.getHost(BROWSER_SANDBOX_PORT);
    const cdpEndpoint = `wss://${host}/ws/automation`;

    const browser = await puppeteer.connect({
      browserWSEndpoint: cdpEndpoint,
      headers: { 'X-Access-Token': sbx.envdAccessToken },
    });
    const page = await browser.newPage();
    await page.goto('https://example.com');
    await page.screenshot({ path: 'example.png' });
    await browser.close();
  } finally {
    await sbx.kill();
  }
}
main();
```

### 第四步：使用代码执行

通过数据面 API 创建上下文并执行代码：

```json
POST ${BASEURL}/sandboxes/{sandboxId}/contexts

{
  "language": "python",
  "cwd": "/home/user"
}
```

```json
POST ${BASEURL}/sandboxes/{sandboxId}/contexts/execute

{
  "contextId": "{contextId}",
  "code": "import json\nprint(json.dumps({'status': 'ok'}))",
  "timeout": 30
}
```

### 在同一会话中协同使用

all in one 模板的核心优势是在同一沙箱会话中同时使用浏览器和代码执行能力。典型工作流：浏览器抓取数据 → Python 代码处理分析 → 文件 API 导出结果。

> **说明**：下方 Python 示例通过 `sbx._envd_access_token` 获取访问 Token，该属性为 SDK 内部实现，后续版本可能变更；JS SDK 可使用公开字段 `sbx.envdAccessToken`。

```python
import asyncio
from e2b import Sandbox
from browser_use import BrowserSession, BrowserProfile

BROWSER_SANDBOX_PORT = 3000

async def run_aio_task():
    # 1. 创建沙箱并获取 CDP 端点
    sbx = Sandbox.create(template="all-in-one-template", api_key=E2B_API_KEY, timeout=600)
    try:
        host = sbx.get_host(BROWSER_SANDBOX_PORT)
        cdp_url = f"wss://{host}/ws/automation"

        browser = BrowserSession(
            cdp_url=cdp_url,
            browser_profile=BrowserProfile(headless=True),
            extra_headers={"X-Access-Token": sbx._envd_access_token},
        )

        # 2. 通过数据面 API 创建 Python 上下文并执行数据处理代码
        #    POST ${BASEURL}/sandboxes/{sandboxId}/contexts
        #    POST ${BASEURL}/sandboxes/{sandboxId}/contexts/execute

        # 3. 用浏览器抓取数据，再用代码处理分析
        #    ...
    finally:
        sbx.kill()

asyncio.run(run_aio_task())
```

## 相关文档

- [沙箱模板概述](../02.内置模板.md)
- [构建模板](../03.构建自定义镜像模板.md)
- [生命周期](../../01.Sandbox/01.生命周期.md)
- [base 模板](base-模板.md)（仅需 envd 基础能力时选择）
- [code-interpreter-v1 模板](code-interpreter-v1-模板.md)（仅需代码执行能力时选择）
- [browser 模板](browser-模板.md)（仅需浏览器自动化能力时选择）
