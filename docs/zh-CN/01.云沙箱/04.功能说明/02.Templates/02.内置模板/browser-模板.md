# browser 模板

browser 模板提供云原生浏览器运行环境，支持通过标准的 Chrome DevTools Protocol（CDP）over WebSocket 远程控制运行在云端隔离容器中的浏览器实例，原生兼容 Puppeteer、Playwright 等主流自动化框架。

browser 模板对齐 E2B 浏览器自动化相关体验，提供 CDP、VNC、截图、页面交互等能力。

## 功能特性

| **特性** | **说明** |
| --- | --- |
| 浏览器自动化 | 内置 Chromium/Chrome 浏览器，支持完整 Web 标准，原生兼容 Puppeteer、Playwright 等自动化框架 |
| CDP 远程控制 | 通过标准 CDP 协议 over WebSocket 精准操控动态渲染页面（SPA），稳定维持登录态与 Session |
| VNC 实时可视化 | 内置 VNC 服务，支持通过 noVNC 客户端实时查看浏览器桌面环境，方便调试和监控 |
| 操作录制 | 支持 VNC 录制功能，可将浏览器操作过程录制为 MKV 视频文件，便于回放和审计 |
| 安全隔离 | 每个 browser 沙箱实例拥有独立的文件系统和进程空间 |
| 传输加密 | 所有数据面端点（CDP 和 VNC）均使用 WSS（WebSocket Secure）协议，全程加密 |

## 适用场景

| **场景** | **说明** |
| --- | --- |
| AI Agent 赋能 | 作为大模型的"眼睛"和"手"，赋予其执行网页浏览、信息提取、在线操作等复杂任务的能力 |
| 数据采集 | 稳定、高效地进行网页抓取，应对动态加载和反爬虫挑战 |
| 自动化测试 | 在云端按需运行端到端（E2E）测试和视觉回归测试，无需维护本地测试环境 |
| 内容生成 | 将动态网页或数据看板自动化生成为 PDF 或截图，用于制作报告和归档 |

## 默认配置

browser 模板的默认配置如下：

| **配置项** | **默认值** | **说明** |
| --- | --- | --- |
| 容器镜像 | `fc-e2b-registry.cn-beijing.cr.aliyuncs.com/runtime/browser:v0.0.33` | 预置 browser 镜像 |
| 默认端口 | 3000 | 沙箱服务监听端口 |
| CPU | 4 vCPU | 最低要求 |
| 内存 | 8192 MB | 最低要求 |
| 磁盘大小 | 10240 MB | 建议 10 GB 以获得充足的临时存储空间，函数计算将默认提供 |

## 快速入门

### 第一步：创建 browser 沙箱

1. 登录 [函数计算控制台](https://fcnext.console.aliyun.com/)。
2. 在**云沙箱**页签下选择**API Keys**, 生成API key。
3. 创建成功后，在服务详情页的**VNC 调试**标签页下**新建沙箱**，获取 CDP 连接端点。

您也可以通过 OpenAPI 或 SDK 进行创建。

### 第二步：准备本地环境

如果您使用 Python SDK 和 Playwright 验证 CDP 连接，可以按以下方式准备本地环境：

```bash
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install 'e2b<2.25.0' 'playwright>=1.49.0' 'python-dotenv>=1.0.0'
```

创建 `.env` 文件并配置以下变量：

```bash
E2B_API_KEY=e2b_xxx
E2B_API_URL=https://api.<region>.e2b.fc.aliyuncs.com
E2B_DOMAIN=<region>.e2b.fc.aliyuncs.com
```

> **说明**：如果同名环境变量已经存在，建议以 `.env` 中的区域配置为准，避免 SDK 连接到错误区域。

### 第三步：创建沙箱并获取连接端点

创建沙箱实例后，通过 SDK 的 `get_host(port)` 方法获取 WebSocket 连接端点。

如果已经通过控制台或 OpenAPI 创建好 browser 模板，可以直接把示例中的 `template` 替换为已有模板名称。如果需要通过 SDK 临时构建模板，可以使用 `Template().from_image()` 从 browser 镜像构建：

```python
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from e2b import Sandbox, Template

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

IMAGE = "fc-e2b-registry.cn-beijing.cr.aliyuncs.com/runtime/browser:v0.0.32"
TEMPLATE_NAME = f"browser-sandbox-{int(time.time())}"
BROWSER_SANDBOX_PORT = 3000


registry_template = Template().from_image(image=IMAGE)
build_info = Template.build(
    registry_template,
    TEMPLATE_NAME,
    api_key=os.environ["E2B_API_KEY"],
    cpu_count=2,
    memory_mb=2048,
)

sbx = Sandbox.create(
    template=build_info.name,
    api_key=os.environ["E2B_API_KEY"],
    timeout=600,
    allow_internet_access=True,
)

host = sbx.get_host(BROWSER_SANDBOX_PORT)

# CDP 自动化端点
cdp_ws_url = f"wss://{host}/ws/automation"

# VNC 实时流端点
vnc_ws_url = f"wss://{host}/ws/livestream"
```

> **说明**：连接 CDP/VNC 端点时需要在请求头中携带 `X-Access-Token` 进行身份验证。使用 SDK 时可通过 `sbx._envd_access_token` 获取该 Token。注意 `_envd_access_token` 属于 SDK 内部属性，后续版本可能重命名或移除；JS SDK 可使用公开字段 `sbx.envdAccessToken`。

### 第四步：连接并执行自动化脚本

将上一步获取的 CDP 端点传入自动化框架脚本中，即可连接到 browser 沙箱并执行任务。

**Python Playwright 连接示例**：

```python
from playwright.sync_api import sync_playwright

headers = {"X-Access-Token": sbx._envd_access_token}

with sync_playwright() as playwright:
    browser = playwright.chromium.connect_over_cdp(cdp_ws_url, headers=headers)
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    page = context.new_page()
    page.goto("https://example.com", wait_until="domcontentloaded", timeout=30000)
    print(page.title())
    page.close()
    browser.close()

sbx.kill()
```

**Puppeteer 连接示例**：

```javascript
const puppeteer = require('puppeteer-core');

const cdpEndpoint = 'wss://<sandbox-host>/ws/automation';
const accessToken = '<access-token>';

async function main() {
  const browser = await puppeteer.connect({
    browserWSEndpoint: cdpEndpoint,
    headers: { 'X-Access-Token': accessToken },
  });

  const page = await browser.newPage();
  await page.goto('https://example.com');
  await page.screenshot({ path: 'example.png' });
  console.log('Screenshot taken!');
  await browser.close();
}

main();
```

**Playwright 连接示例**：

```javascript
const { chromium } = require('playwright-core');

const cdpEndpoint = 'wss://<sandbox-host>/ws/automation';
const accessToken = '<access-token>';

async function main() {
  const browser = await chromium.connectOverCDP(cdpEndpoint, {
    headers: { 'X-Access-Token': accessToken },
  });

  const page = await browser.newPage();
  await page.goto('https://example.com');
  await page.screenshot({ path: 'example.png' });
  console.log('Screenshot taken!');
  await browser.close();
}

main();
```

## WebSocket 端点说明

browser 模板提供两个 WebSocket 端点，用于不同的自动化场景：

| **端点** | **路径** | **用途** |
| --- | --- | --- |
| 健康检查端点 | `https://<sandbox-host>/health` | 判断 browser 服务是否启动完成 |
| CDP 自动化端点 | `wss://<sandbox-host>/ws/automation` | 浏览器自动化，与 Puppeteer 和 Playwright 兼容 |
| VNC 实时流端点 | `wss://<sandbox-host>/ws/livestream` | 实时查看浏览器桌面环境，支持通过 noVNC 客户端查看 |

> **说明**：`<sandbox-host>` 通过 SDK 的 `sbx.get_host(3000)` 获取。所有端点均需在请求头中携带 `X-Access-Token` 进行身份验证。

在沙箱内部可以先探测 CDP WebSocket 握手是否正常。如果返回 `101 Switching Protocols`，说明 CDP 端点已经可升级为 WebSocket 连接：

```bash
curl -sS -m 4 -i \
  -H 'Connection: Upgrade' \
  -H 'Upgrade: websocket' \
  -H 'Sec-WebSocket-Version: 13' \
  -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' \
  http://localhost:3000/ws/automation
```

您可以使用 `wscat` 工具直接与 CDP 端点交互，发送原始 CDP 命令进行调试：

```bash
# 安装 wscat
npm install -g wscat

# 连接到 CDP 代理（host 通过 sbx.get_host(3000) 获取）
wscat -c "wss://<sandbox-host>/ws/automation" -H "X-Access-Token:<access-token>"

# 发送 CDP 命令
{"id":1,"method":"Runtime.evaluate","params":{"expression":"navigator.userAgent"}}
```

## VNC 实时查看

browser 模板支持通过 VNC 实时查看远程浏览器的桌面环境，方便在开发和调试阶段监控自动化任务的执行情况。

### 使用在线 noVNC 客户端

1. 访问 noVNC 官方提供的在线客户端：[https://novnc.com/noVNC/vnc.html](https://novnc.com/noVNC/vnc.html)
2. 在连接设置中，**高级** > **WebSocket** 中填入以下连接信息：
   - **主机**：通过 `sbx.get_host(3000)` 获取的 host 地址
   - **端口**：`443`
   - **路径**：`ws/livestream`
3. 点击**连接**，即可看到浏览器界面。

> **说明**：noVNC 连接同样需要通过 `X-Access-Token` 进行身份验证。

> **说明**
>
> 连接成功后，初始界面可能为黑屏或灰屏。这是正常现象，因为浏览器正在等待指令。当您的自动化脚本执行 `page.goto()` 等操作后，界面才会显示相应内容。

## 框架集成

以下示例聚焦框架接入方式。实际运行前，请先按快速入门中的流程创建 browser 沙箱，并获取 `cdp_url` 和 `X-Access-Token`。

### BrowserUse 集成

BrowserUse 是专门为 AI Agent 设计的浏览器自动化框架，通过 browser 模板可以在云端运行：

```python
import asyncio
from e2b import Sandbox
from browser_use import Agent, BrowserSession
from browser_use.llm import ChatDeepSeek
from browser_use.browser import BrowserProfile

BROWSER_SANDBOX_PORT = 3000

async def main():
    sbx = Sandbox.create(template="browser-sandbox-template", api_key=E2B_API_KEY, timeout=600)
    host = sbx.get_host(BROWSER_SANDBOX_PORT)
    cdp_url = f"wss://{host}/ws/automation"

    browser_session = BrowserSession(
        cdp_url=cdp_url,
        browser_profile=BrowserProfile(
            headless=False,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            timeout=3000000,
            keep_alive=True,
        ),
        extra_headers={"X-Access-Token": sbx._envd_access_token},
    )

    llm = ChatDeepSeek(api_key="sk-your-deepseek-sk")

    agent = Agent(
        task="请访问 https://www.aliyun.com/product/list 并分析阿里云提供的产品分类",
        llm=llm,
        browser_session=browser_session,
        use_vision=True
    )
    result = await agent.run()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### LangChain 集成

通过 E2B SDK 可以将 browser 模板轻松集成到 LangChain Agent 中：

```python
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from e2b import Sandbox
from playwright.async_api import async_playwright

BROWSER_SANDBOX_PORT = 3000

# 创建沙箱并获取 CDP 端点
sbx = Sandbox.create(template="browser-sandbox-template", api_key=E2B_API_KEY, timeout=600)
host = sbx.get_host(BROWSER_SANDBOX_PORT)
cdp_url = f"wss://{host}/ws/automation"
headers = {"X-Access-Token": sbx._envd_access_token}

@tool
def navigate_and_extract(url: str) -> str:
    """导航到指定 URL 并提取页面文本内容"""
    import asyncio
    async def _run():
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(cdp_url, headers=headers)
            page = browser.contexts[0].pages[0] if browser.contexts[0].pages else await browser.contexts[0].new_page()
            await page.goto(url, wait_until="networkidle")
            content = await page.content()
            return content[:5000]
    return asyncio.run(_run())

llm = ChatOpenAI(model="qwen-max", api_key="sk-your-key", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

agent = create_react_agent(
    model=llm,
    tools=[navigate_and_extract],
)

async def run_agent():
    result = await agent.ainvoke({
        "messages": [
            HumanMessage(content="请访问新浪财经，查询腾讯控股今日的股价")
        ]
    })
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_agent())
```

## 使用限制

| **限制项** | **约束** |
| --- | --- |
| 会话生命周期 | 单个沙箱会话的默认最长生命周期为 6 小时，到期后自动销毁 |
| 浅休眠超时 | 可通过 `sandboxIdleTimeoutSeconds` 参数设置，超时无操作后提前终止 |
| 浏览器支持 | 目前内置 Chromium/Chrome 浏览器 |
| 代码解释器 | browser 模板包含 E2B envd 兼容基础能力，但不提供 Code Interpreter 服务，不能通过 Code Interpreter 上下文直接执行 Python |

## 相关文档

- [沙箱模板概述](../02.内置模板.md)
- [创建沙箱](../../01.Sandbox/02.创建沙箱.md)
- [生命周期](../../01.Sandbox/01.生命周期.md)
- [base 模板](base-模板.md)（仅需 envd 基础能力时选择）
- [code-interpreter-v1 模板](code-interpreter-v1-模板.md)（仅需代码执行能力时选择）
- [all in one 模板](all-in-one-模板.md)（需要同时使用浏览器和代码执行能力时选择）
