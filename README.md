# 为中国大陆等地区开通 Apple Watch 高血压通知

[English](README.en.md)

**手表支持，但“健康”里提示所在地区不可用？让 AI 帮你开通，结束后确认真实定位已恢复。**

这个 Skill 面向**中国大陆等尚未开放高血压通知的地区**。AI 自动执行本地开通流程：通过 Mac 连接 iPhone，临时提供香港定位，协助完成健康设置；需要你插线、解锁或回答问题时，AI 会提示并等待。

**优先提供 WorkBuddy、Codex 的使用入口**，也支持 Claude Code 等本地 Agent。若你所在地区已支持、能在“健康”中正常开启，直接按 [Apple 官方步骤](https://support.apple.com/en-us/117296)设置即可。

## 先准备这些

- 一台 **Mac**，装有能在本机执行操作的 **WorkBuddy 或 Codex**。
- 支持高血压通知的 **Apple Watch**，以及与它配对的 **iPhone**。
- 一根能传输数据的 **USB 数据线**。

不需要提前安装 Python、Git 或 Homebrew。功能仍需满足 Apple 的[机型、系统和使用资格要求](https://support.apple.com/en-us/117296)；本工具不能让不支持的硬件获得该功能。

## 安装：选你正在用的 AI

### WorkBuddy

1. 打开[下载页](https://github.com/flute/apple-watch-hypertension-skill/releases/latest)，在 **Assets** 中下载 **apple-watch-hypertension-workbuddy.zip**。
2. 打开 WorkBuddy 的技能管理，选择**添加技能 / 导入 ZIP**，导入这个文件，不用解压。
3. 新开对话，发送下一节的指令，让它准备环境并开始检查。

找不到导入按钮，或提示无法执行本地命令？看[新手教程：WorkBuddy](references/beginner.zh-CN.md#workbuddy)。

### Codex

1. 在[下载页](https://github.com/flute/apple-watch-hypertension-skill/releases/latest)下载 **apple-watch-hypertension.zip**，双击解压。
2. 按 **⌘ + 空格**，输入“终端”，回车打开。
3. 输入 `bash `，注意末尾留一个空格。把解压文件夹中的 **install.command** 拖进终端，再按回车。
4. 输入 **1** 并回车，等到显示“安装完成”。然后在 Codex 新开对话。

安装程序会自动准备 Python 和依赖。不会使用终端？看[一步一步的新手教程](references/beginner.zh-CN.md#codex)。

**Claude Code / 其他 Agent：**见[适配说明](references/agents.md)。豆包、DeepSeek 的普通网页和手机聊天不支持直接安装执行本 Skill。

## 装好后，把这句话发给 AI

> 使用 apple-watch-hypertension，帮我开通因地区限制不可用的 Apple Watch 高血压通知。先检查设备并准备本地运行环境。我同意通过 USB 临时使用香港定位；需要我操作时请提示并等待。结束后停止发送，确认真实定位恢复，再确认高血压通知仍开启。

接下来按提示连接手机、解锁，并如实回答健康设置中的问题。**你不需要看懂代码或通信协议。**

## 怎样才算完成

AI 会依次确认：

1. 地图中的当前位置已临时切换到香港。
2. “健康”中的高血压通知已开启。
3. 定位发送已停止，你已拔掉数据线。
4. 地图回到真实位置，重新打开“健康”后通知仍开启。

缺少任何一项，就不能算完整开通。中途想退出，告诉 AI：**“停止发送，恢复真实定位。”**

## 使用前了解

- 这是**高血压通知**，不会显示血压数值，也不能代替诊断。
- 使用本地 USB 流程，**不依赖 AnyGo 云端**。证书和私钥不随项目发布，由 AI 按说明在本机准备；实验身份可能失效。
- 已在一次 **S12 + Codex** 实操中完成开通、恢复定位和通知复查。WorkBuddy 已适配技能导入格式，尚未完成实机验证。不同机型、系统和地区不能保证都成功。
- 地区支持会变化，以 [Apple 当前列表](https://www.apple.com/watchos/feature-availability/#health-hypertension-notifications)为准。

[新手教程与排错](references/beginner.zh-CN.md) · [Agent 适配表](references/agents.md) · [实操复盘](references/retrospective.md) · [技术手册](references/operations.md) · [代码来源](THIRD_PARTY_NOTICES.md)

GPL-3.0-only。独立开源项目，与 Apple 无隶属关系。
