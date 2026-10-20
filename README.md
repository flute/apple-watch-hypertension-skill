# Apple Watch 高血压通知 Skill

[English](README.en.md)

**让 AI 帮你检查、设置并核验 Apple Watch 高血压通知。**

支持在 Mac 上使用 Codex、Claude Code、WorkBuddy 等 Agent。能自动做的就自动做；需要插线、解锁或回答健康问题时，会告诉你并等待。完成后停止定位发送，确认真实位置恢复、通知仍开启。

> 这是“高血压通知”，不是血压测量。需要兼容的手表、系统和使用资格；地区限制或设备变化可能导致无法开通，不保证所有 Apple Watch 都能成功。

## 安装

下载这个仓库，选一种方式：

```sh
git clone https://github.com/flute/apple-watch-hypertension-skill.git
cd apple-watch-hypertension-skill

# Codex
python3 scripts/install.py --agent codex

# Claude Code
python3 scripts/install.py --agent claude
```

**WorkBuddy：**从 [Releases](https://github.com/flute/apple-watch-hypertension-skill/releases) 下载 `apple-watch-hypertension-workbuddy.zip`，在技能页面导入 ZIP。

其他支持 `SKILL.md` 的 Agent，可以使用 `python3 scripts/install.py --target /你的/skills/目录`。安装后重新加载技能或新开对话。Skill 不会给 Agent 增加本来没有的 USB 或手机控制能力。

## 怎么用

把下面这句话发给 Agent：

> 使用 apple-watch-hypertension，帮我检查并开通 Apple Watch 高血压通知。若需要，我同意用本地 USB CarKit 临时提供香港定位。需要我操作时请告诉我并等待；结束后确认真实位置恢复，而且通知仍开启。

准备好：**Mac、与手表配对的 iPhone、USB 数据线、[uv](https://docs.astral.sh/uv/getting-started/installation/)**。Agent 会检查其余条件并安装固定版本的依赖。没有手机控制工具也能用，手机上的步骤由你完成、确认。

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
