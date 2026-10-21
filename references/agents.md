# Agent 适配：先看执行位置，再看模型品牌

“支持 Skill”“模型会调用工具”“能操作这台 Mac 的 USB”是三个独立条件。把 Markdown 发到聊天框不会自动安装本机执行能力。

| 产品/模式 | 安装或使用方式 | 能力边界与验证状态 |
| --- | --- | --- |
| WorkBuddy，Mac 本地执行 | 专用 ZIP 导入；在实际工具目录准备环境 | 官方导入字段已适配；未逐版本导入/实机验证；必须实查本地命令权限 |
| Codex，本地 Mac 执行 | install.command 选 1；用户目录 ~/.agents/skills | 已适配目录；本会话在 Codex 宿主完成实机流程，发布脚本另做离线测试 |
| Claude Code，Mac 本地终端 | 选 2；~/.claude/skills | 官方技能目录已适配，未在此宿主实机验证 |
| DeepSeek 模型接入 Claude Code / 其他本地 Agent | 按宿主安装，模型由用户按官方说明配置 | 官方提供 Agent 接入文档；本项目未实测该模型组合，工具权限由宿主提供 |
| 豆包模型通过火山方舟接入本地编程 Agent | 按宿主安装；确认账户、模型和宿主支持 | 官方有编程工具接入说明；本项目未实测，不能据此宣称豆包聊天 App 兼容 |
| 豆包 / DeepSeek 普通网页、手机聊天 | 阅读教程、解释错误、指导用户手动操作 | 未提供/验证本项目可用的本机 Mac USB 执行入口，不列为直接自动开通支持 |
| 其他 Mac Agent：OpenCode、CodeBuddy、Qoder 等 | 先查该版本官方 Skill 导入/目录；选 4 指定父目录或让其读本地 SKILL.md | 条件适配，未实机验证；不猜目录，不假设格式相同 |
| 云端 Agent、远程 Linux 容器、Windows 主机 | 可做文档指导；需另有 Mac 端执行器 | 本项目没有远程桥接服务；不能直接访问用户 Mac USB |

核对日期：2026-10-20。产品会变化；“未验证”不表示永远不支持，也不能换成已兼容的承诺。手机 GUI 自动化不是必须条件，可以人工配合；Mac 端进程执行和停止能力则是自动流程的必要条件。

## 豆包、DeepSeek 用户怎么选

**已有本地 Agent：**通常不需要为了本 Skill 更换模型。先检查它能否读取技能文件、在连接 iPhone 的 Mac 上运行命令、跟踪/停止后台进程，并等待你的明确回答。满足后按宿主安装，而不是按“豆包/DeepSeek”创建一个猜测的技能目录。

**想用 DeepSeek API：**可参考 [DeepSeek 官方 Claude Code 接入指南](https://api-docs.deepseek.com/quick_start/agent_integrations/claude_code/)。API 账户、费用和配置与本项目独立。只在本地配置密钥，不把密钥发给聊天或写入 Skill。模型名/接口可能变化，本文不复制易过期的配置命令。

**想用豆包 API：**参考[火山方舟编程工具接入说明](https://docs.volcengine.com/docs/82379/2479140?lang=zh)。这指模型接入编程宿主，不代表豆包手机助手、网页版或所有“工作模式”都有 Mac 本地权限。只有连接同一台 Mac 的执行器并通过检查后才进入设备流程。

**只有普通聊天：**可以让聊天产品解释[新手指南](beginner.zh-CN.md)和[操作手册](operations.md)，但每个本地命令都要由你执行、把脱敏结果反馈给它。先用安装菜单 3 准备工具。不要让模型编造“已执行”“已开通”，也不要上传身份凭据。由于发送有时限、恢复需要核验，小白更适合有本机执行工具的宿主；这是需要人工执行命令的专家协助模式，新手指南不提供独立的全程手动命令向导；不列为小白可独立完成或一键自动化支持。

## 交给新宿主的能力检查

Agent 必须先回答：

1. 命令实际运行在用户连接 iPhone 的 Mac，还是云端？
2. 能否读到 SKILL.md、references 和 scripts 的完整绝对路径？
3. 能否准备独立 Python 3.11 环境并运行 doctor？仅安装导入成功不够。
4. 能否保存 session ID、查看状态、执行停止，在等待用户时管理截止时间？
5. 没有手机控制时，能否一次提出一个明确操作并等待？
6. 能否在错误、取消、超时后停止发送，要求拔线、恢复并验证真实位置和通知？

不满足的项要明确交给人或停止在检查阶段。不能把未知项默认填“支持”。执行授权遵循宿主现有机制，不要求关闭整套安全权限。

## Official references / 官方来源

- [Codex Skills](https://learn.chatgpt.com/docs/build-skills)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [WorkBuddy 自定义技能](https://open.workbuddy.cn/docs/skill)
- [DeepSeek Agent integrations](https://api-docs.deepseek.com/quick_start/agent_integrations/claude_code/)
- [火山方舟编程工具接入](https://docs.volcengine.com/docs/82379/2479140?lang=zh)
- [uv installation](https://docs.astral.sh/uv/getting-started/installation/) and [managed Python](https://docs.astral.sh/uv/guides/install-python/)

## English summary

Install for the **local execution host**, not the model brand. Codex and Claude Code have supported skill layouts; WorkBuddy has a tailored import ZIP. Only Codex-hosted hardware operation was observed in this session; other hosts/model combinations remain unverified. DeepSeek officially documents local-agent integrations; Volcengine documents coding-tool integrations for its model services. Neither proves ordinary Doubao/DeepSeek chat can execute Mac USB commands.

Cloud execution, Windows, or phone chat needs a separate Mac-side executor, which this project does not provide. With chat-only products a person must run every local command and confirm every phone observation. Check filesystem, local shell, process control and human-wait capabilities before promising automation.
