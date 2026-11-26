---
name: skillhub
description: Manage and share Agent skills between compatible tools on the same computer. Use when installing, listing, deduplicating, deleting or restoring local skills, or connecting local Agent skill directories.
---
# SkillHub v0.4.0 — 本机测试版

目标：在同一台电脑、同一系统用户下，让兼容的本地 Agent 共用技能。只处理真实本机文件；云端沙箱不是用户电脑。本版本不配置或执行远端同步，不默认创建后台任务。已有远端配置和文件保留，但不会拉取或推送；旧版已注册的定时任务不会自动移除，升级时应检查并向用户说明。

## 初始化
1. 确认当前运行环境能访问用户真实电脑。不能访问时停止并说明需要在本地 Agent 中运行；不把沙箱结果称作本机结果。
2. 使用随技能发布的完整脚本和测试文件，运行 `python3 scripts/manager.py setup`。它扫描 ~/.agents/skills 和已存在的 ~/.codex/skills、~/.claude/skills、~/.dsh/skills、~/.zcode/skills；额外目录只有在确认是该 Agent 的技能目录时才用 `--adapter 路径` 添加。项目目录用 `--project 路径` 登记，保持项目隔离。不要声称候选路径已经被宿主加载。
3. 报告扫描结果、冲突和无法处理的项目；先检查来源、内容与敏感信息，然后用 `setup --approve-import` 收录安全的全局技能。同名不同内容不覆盖；原始目录被替换为链接时保留备份。已有 ~/.skill-manager 库与配置继续复用。目录不可写或符号链接失败时报告原因。
4. 运行自检并输出目录。让用户在每个 Agent 中开启新会话或刷新，然后实际调用一个安全技能；分别记录成功、失败或未验证。扫描到目录、建立链接和隔离自检均不等于真实加载成功。

## 安装与管理
- 新增技能前运行 `python3 scripts/manager.py catalog`；检查来源和内容，按名称及内容核对。使用 `python3 scripts/manager.py install 技能目录 --approved --origin self|third-party|modified|unknown` 收录；先审查，不运行第三方安装脚本。项目技能不提升为全局。
- 安装或变更后运行 `python3 scripts/manager.py catalog`，列出全局和项目技能，标记未纳管、冲突、实际新增及有证据的自建技能。历史来源不明就标记未知。
- `sync` 在本版仅扫描和建立本机链接；`sync --approve-import` 会批量收录扫描到的安全全局目录，使用前须审查。它不能拦截其他工具的原生安装流程。
- `delete 名称` 仅逻辑删除已纳管全局技能，保留内容与删除记录；`restore 名称` 恢复。删除前确认目标和影响；项目技能、未纳管文件和 SkillHub 自身不能由此命令删除。完成后重新读取目录。
- 技能目录以紧凑的全局、项目两组展示；每项显示名称，确有依据才显示 NEW 或自建。宿主无真实交互回调时，用文字命令说明删除方式，不伪造按钮。

只报告实际执行和验证的结果。每个 Agent 的发现规则、权限和刷新时机可能不同；自动触发安装、跨电脑、ChatGPT 网页、云端同步和后台定时同步均不属于本版已验证能力。
