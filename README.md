# Apple Watch 高血压通知 Skill

[English](README.en.md)

**让 AI 帮你检查、设置并核验 Apple Watch 高血压通知。**

支持在 Mac 上使用 Codex、Claude Code、WorkBuddy 等 Agent。能自动做的就自动做；需要插线、解锁或回答健康问题时，会告诉你并等待。完成后停止定位发送，确认真实位置恢复、通知仍开启。

> 这是“高血压通知”，不是血压测量。需要兼容的手表、系统和使用资格；地区限制或设备变化可能导致无法开通，不保证所有 Apple Watch 都能成功。

## 安装

**第一次用？从[完整新手教程](references/beginner.zh-CN.md)开始**：如何下载、打开终端、拖入文件、选择 Agent，以及报错、更新和卸载，都写在里面。

不需要先装 Python、Git、Homebrew 或 Xcode：

1. 从[最新发布页](https://github.com/flute/apple-watch-hypertension-skill/releases/latest)下载 **apple-watch-hypertension.zip** 并解压。
2. 按 **⌘ + 空格**，输入“终端”，回车打开。
3. 输入 `bash `（后面留一个空格），把解压目录里的 **install.command** 拖进终端，回车。
4. 输入 **1** 安装到 Codex，**2** 安装到 Claude Code；其他模式看教程。程序会准备独立 Python 3.11 和固定依赖。
5. 看到“安装完成”后，重新打开 Agent 对话。安装本身不会连接手机或开启定位。

**WorkBuddy：**下载 **apple-watch-hypertension-workbuddy.zip**，在技能管理里导入；本地运行环境仍需准备，按[详细步骤](references/beginner.zh-CN.md#5-workbuddy-怎么装)完成。

**豆包 / DeepSeek：**普通聊天可以指导你；能否自动执行取决于有没有连接这台 Mac 的本地工具。DeepSeek 等模型接入 Claude Code 等本地 Agent 时，按宿主安装。详见[适配表与选择建议](references/agents.md)，不把“能聊天”当成“能操作 USB”。

## 怎么用

把下面这句话发给 Agent：

> 使用 apple-watch-hypertension，帮我检查并开通 Apple Watch 高血压通知。若需要，我同意用本地 USB CarKit 临时提供香港定位。需要我操作时请告诉我并等待；结束后确认真实位置恢复，而且通知仍开启。

准备好：**Mac、与手表配对的 iPhone、USB 数据线**。安装程序准备运行环境，Agent 检查其余条件。没有手机控制工具也能用，手机上的步骤由你完成、确认。

## 它会怎么做

1. 检查兼容性和当前状态；已开启就不重复操作，能直接设置就直接设置。
2. 确有需要且你同意时，用本地 MFi-v3 认证和 USB CarKit 发送香港 NMEA，**不依赖 AnyGo 云端**。
3. 在地图确认定位生效，再完成健康设置。健康问题按你的实际情况填写。
4. 停止发送、拔线、确认真实位置恢复，再核对通知仍开启。缺少任何一项就不会报“全部完成”。

证书和私钥**不在仓库里**。可使用自己的匹配身份，或让 Agent 按提示从指定 DiPlay APK 本地提取实验身份。凭据只保存在你的 Mac；实验身份可能失效。发送进程禁止 IP 联网，单次最多运行十分钟。

## 验证与限制

本流程在一次 S12 实操中成功完成了开通和恢复核验；发布版脚本通过离线测试。Claude / WorkBuddy 的安装结构已适配，尚未逐一实机验证。详情见[实操复盘](references/retrospective.md)和[操作手册](references/operations.md)。

开发检查（仅源码仓库）：`uv sync --frozen && uv run pytest -q && uv run ruff check scripts tests`

[Apple 官方说明](https://support.apple.com/en-us/117296) · [地区与机型支持](https://www.apple.com/watchos/feature-availability/#health-hypertension-notifications) · [代码来源与许可证](THIRD_PARTY_NOTICES.md)

GPL-3.0-only。独立开源项目，与 Apple 无隶属关系。
