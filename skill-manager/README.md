# Skill Manager v0.3.1 — 本地优先试用版

适用于具备本机文件和终端权限的 Agent。无需独立 APP。Python 3.9+；GitHub 同步需 Git、网络、已有 Git 凭据和专用私有仓库。macOS 可选择创建系统定时任务，Windows/Linux 本地核心脚本可运行但系统任务需手动配置，未实测。

## 安装
解压后，在本地 Agent（例如 Codex）中说：

> 请将这个 skill-manager 文件夹安装到 ~/.agents/skills/skill-manager，读取 SKILL.md，按说明初始化，自动执行自检。先检查已有目录和敏感文件，再征求我的 GitHub 仓库和上传授权。

也可以在 macOS 终端执行（当前目录为解压后的父目录；已有同名目录时不要覆盖）：

```sh
mkdir -p ~/.agents/skills
[ ! -e ~/.agents/skills/skill-manager ] && [ ! -L ~/.agents/skills/skill-manager ] && cp -R skill-manager ~/.agents/skills/skill-manager
python3 ~/.agents/skills/skill-manager/scripts/manager.py setup
```

上面仅本地初始化与预览，不上传。若计划使用 GitHub，建议第一次 setup 就提供专用私有仓库地址（本地预览会创建空目录，不会阻碍连接）。已有非空本地库时需要人工迁移；不要覆盖它。

授权后运行（将 OWNER/REPO 替换为自己的专用私有仓库）：

```sh
python3 ~/.agents/skills/skill-manager/scripts/manager.py setup --remote https://github.com/OWNER/REPO.git --confirm-private --approve-import --schedule
```

`--approve-import` 是批量导入及上传授权，并允许将现有同内容目录迁移为符号链接，保留原件备份。请先审查清单、许可证、私密内容。敏感模式检测只是辅助，不能保证识别全部秘密。定时任务若带此参数，也会导入未来扫描到的文件；不希望长期自动导入请不要一起开启这两个选项（可先批准同步，再不带批准标记设置定时任务）。专用仓库必须是可信的，只用于 Skill Manager；不要指向已有项目仓库。

## 日常使用
对 Agent 说“安装这个 Skill，先调用 Skill Manager 查重”“同步技能库”“展示我的技能”“运行 Skill Manager 自检”。

- 权威库：`~/.skill-manager/library/skills/`，有 GitHub 时为私有库克隆。
- 本机共享入口：`~/.agents/skills/`（符号链接指向权威文件）。匹配的原目录迁移时保留 `~/.skill-manager/backups/`，并非永久只有一个物理副本；备份不参与加载。
- 管理数据：`~/.skill-manager/library/records/`；日志 `~/.skill-manager/events.jsonl`。
- 安装时间：记录首次收录时间；原始创建时间和调用次数不可可靠获取。
- 新 Agent：若支持共享路径，可直接读取；其他路径通过 `setup --adapter /已验证的目录` 注册。不自动修改未知 Agent 配置。
- 项目级：通过 `setup --project /项目路径` 识别并记录，本版不上传项目内容。
- 删除：逻辑删除，撤除已管理的链接，保留数据和删除记录；未受管理的副本不自动删除。
- 冲突：不自动合并或覆盖，需人工检查。Git 非快进时停止，避免丢失。
- macOS 定时同步：`--schedule` 创建 LaunchAgent，每 300 秒运行，真实执行依赖设备在线、系统调度和 Git 认证。日志位于 `~/.skill-manager/scheduler.err` 和 `scheduler.out`。取消：`launchctl bootout gui/$(id -u)/local.skill-manager.sync` 后移除 `~/Library/LaunchAgents/local.skill-manager.sync.plist`。更新任务前请先取消旧任务，再重新授权注册。

## 尚未实现或未验证
原生安装前后钩子无法在所有 Agent 强制执行；任意工具自动发现仍需适配；网页端无法通用地直接安装其他 Skill，仅提供授权动态读取/人工导入流程；真实 GitHub 和跨电脑调度尚未测试；修改版本需人工解决冲突。自检使用隔离测试目录及本地裸 Git 仓库，不会替代实际设备测试。

## V0.3 安装后自动展示目录
每次由 Manager 处理安装后，Agent 必须根据实际 catalog 输出完整的简洁技能目录：不展示顶部汇总数据或统计卡片；仅按全局/项目分组，以自适应紧凑多列网格展示完整技能名称；每项独立，自建标签紧邻可见删除按钮，新增标记 NEW，停用、未纳管等状态行内标注。可主动运行 `python3 scripts/manager.py catalog`。覆盖统一库及已配置本地目录，不代表所有云端账户或未知 Agent；定时任务不能主动在任意 Agent 的对话里显示消息。


## V0.3 changes
Local-first initialization; GitHub is optional. Ask once whether cross-computer use is needed, configure a supplied and authorized destination only. Windows Task Scheduler registration added (requires real-device validation); macOS and Windows scheduled scans default to pending review. Existing Git metadata is excluded from import, not copied. Catalog includes provenance (self, third-party, modified, unknown); use `install PATH --approved --origin third-party --source-url URL` or `origin NAME self` for confirmed attribution. Existing skills without evidence remain unknown. Cloud-folder transport and migration of populated local libraries to GitHub are not implemented in this revision. Native install interception remains platform-dependent. V0.3 has not been executed in a real device environment yet.

目录样式：宽屏 3–4 列、普通面板 2 列、窄屏 1 列；每项为独立紧凑横条，名称可换行，不显示汇总数字、不使用高卡片、不另按来源分组。仅确认自建的 Skill 显示「自建」文字，置于垃圾桶图标之前。删除按钮直接显示，无省略号菜单、无停用开关。支持真实操作的宿主可在确认后调用已有 delete 命令并重新读取 catalog；当前底层仅支持已纳管且无歧义的全局 Skill 逻辑删除，项目级或未纳管文件需另行验证和授权。无真实操作能力的宿主使用自然语言命令，不伪造点击删除。保留恢复能力。
