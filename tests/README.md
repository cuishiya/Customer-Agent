# Windows 手动测试指南

按 1–6 步依次完成。所有命令都在包含 `app.py` 的项目文件夹中运行，无需使用固定的绝对路径。第 1–2 步配置环境与模型，第 3 步接通拼多多店铺，第 4–6 步用买家账号测试 Agent 功能。

## 1. 配置环境、启动程序并设置 LLM

先下载或解压项目源码，确认项目文件夹中有 `app.py`、`pyproject.toml` 和 `uv.lock`。需要 Windows 图形桌面、uv、Python 3.11、Chrome 或 Edge，以及安装依赖和连接 LLM／拼多多所需的网络。Python 3.11 由 uv 安装，PyQt6、Playwright、LiteLLM 等项目依赖由 `uv sync` 安装。

在 PowerShell 运行 `uv --version`。如提示找不到命令，先安装 uv：

```powershell
winget install --id astral-sh.uv -e
```

安装后关闭并重新打开 PowerShell，再运行 `uv --version`，检测是否安装成功。

终端打开项目文件夹。然后安装 Python 3.11 和依赖并启动：

```powershell
uv python install 3.11
uv sync --python 3.11 --locked
uv run python --version
uv run python app.py
```

`uv sync` 会根据 `uv.lock` 把 PyQt6、Playwright、LiteLLM 等依赖安装到项目的 `.venv`；版本检查应显示 **Python 3.11.x**。以后启动只需 `uv run python app.py`，无需手动激活虚拟环境。

打开应用的「设置 → LLM 模型配置」，选择模型供应商，填写**模型名称**和 **API Key**。使用 OpenAI-compatible 接口时还要填写 **API Base URL**；所选模型需支持工具调用。点「保存」，看到保存成功提示。请把密钥留在设置页，不要写进测试命令。随后按第 2 步验证实际问答。

## 2. 在新终端验证 LLM 问答

保持应用运行。再次从项目文件夹的资源管理器地址栏输入 `powershell`，打开第二个终端。先设置 UTF-8，避免通过管道传递中文时变成 `?`：

```powershell
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONIOENCODING = 'utf-8'
```

随后**整块复制**以下命令。`@'` 和 `'@` 都要单独占一行：

```powershell
@'
import asyncio
from Agent.CustomerAgent.custom.customer_agent import CustomerAgent

async def main():
    agent = CustomerAgent()
    try:
        question = "你好，请用一句话介绍你能帮我做什么？"
        reply = await agent.async_reply(question)
        print("问题：", question)
        print("回答：", reply.content)
    finally:
        await agent.close()

asyncio.run(main())
'@ | uv run python -
```

检查“问题”能正常显示中文，“回答”是自然语言，且不是“AI 服务暂时不可用”或“初始化失败”。修改 `question` 可再测一轮。此命令没有店铺和商品上下文，只用于确认模型能完成一问一答；后三项功能要用第 3 步的真实会话验证。

## 3. 创建拼多多账号并启动自动回复

1. 准备一个**拼多多商家账号**和另一个**买家账号**。商家店铺至少有一件审核通过的在售商品，并能在拼多多客服聊天中接收买家消息。
2. 在应用「账号管理 → 添加账号」选择“拼多多”，输入商家账号登录信息，完成登录与验证。账号应出现在列表中。
3. 到「自动回复」找到该账号，依次点「上线」和「开始回复」，确认状态为在线且正在回复。若刚修改过 LLM 配置，先停止再重新启动自动回复，让新配置生效。
4. 用买家账号从店铺或商品页发一条普通消息。买家应收到自动回复；同时可在应用「日志管理」核对处理记录。第 4–6 步均在这个店铺会话中测试。

## 4. 验证产品知识库

1. 在「知识库 → 产品知识」点「同步产品知识」，确认在售商品出现在列表中。
2. 打开其中一件商品的「详情」，核对“提取知识”的名称、规格等内容；有缺漏时按真实商品页面补充并保存。
3. 买家从该商品页提问示例问题，核对回复是否与对应商品知识一致，是否编造未提供的价格、库存、材质或功效。

如果回答很笼统，先检查是否选对店铺、商品是否同步成功，以及知识内容是否已保存。

## 5. 验证客服知识库

1. 在「知识库 → 客服知识」点「批量导入」，选择 [客服知识示例.xlsx](data/customer_service_knowledge.xlsx)。应导入 **4 条**，且全部启用。
2. 买家逐条提问，并与导入内容比对：

| 买家提问             | 应核对的内容                                 |
| -------------------- | -------------------------------------------- |
| 怎么申请退货？       | 引导从订单进入售后申请，不擅自承诺运费或结果 |
| 运费在哪里看？       | 以收货地址和结算页显示为准                   |
| 优惠券为什么不能用？ | 核对有效期、适用商品及订单金额               |
| 商品尺寸在哪里确认？ | 引导查看商品当前可选规格                     |

测试结束后，可删除导入的示例知识。

## 6. 验证关键词功能

1. 打开「关键词管理」，确认已有“转人工”；没有就点「添加关键词」创建。
2. 买家发 `转人工`，查看会话与「日志管理」是否进入转接流程。
3. 再发一句不含关键词的普通商品问题，确认没有误触发转接。

真正转给人工需要店铺另有一位**在线且可接待的客服**。只有一个客服账号时，重点检查关键词是否命中、是否提示无可转接客服。
