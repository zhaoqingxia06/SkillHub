# 更新日志

## 0.4.0 本机测试版

- 聚焦同一台电脑上兼容 Agent 的技能扫描、去重、共享、删除与恢复。
- 暂停远端拉取和推送，即使旧库已经配置 Git；保留原有数据和配置。
- 不默认创建定时任务；已有旧任务不会自动移除。真实 Agent 发现和加载需分别验收。
- 保留项目隔离、冲突保护与原始文件备份。

## 0.3.3

- 强化目录展示规则：每个技能保留独立删除入口，非交互宿主使用明确的文本操作提示；未纳管和受保护条目不可假装可删除。
- 首次扫描但未完成入库时明确标识为部分初始化；本地纳管与远端上传分别授权。
- 简化安装反馈，补充历史自建来源核验、版本更新及私有仓库同步验证规则。
- 本次为执行规则修订，尚未验证各宿主交互能力。

## 0.3.2

- 统一产品名称、Skill 标识及源码目录为 SkillHub / `skillhub`。
- 首页改为中文，移除重复使用说明；执行规则统一维护在 SKILL.md。
- 保留旧版数据目录和定时任务标识以兼容升级；新旧名称均禁止作为普通技能误收录或删除。尚未重新执行测试。

## 0.3.1

- Simplified the skill directory into a responsive, compact grid grouped by global and project scope.
- Removed aggregate metrics and visible disable controls; added inline self-created and NEW labels.
- Defined independent delete controls with confirmation, verified catalog refresh, and recovery. Interactive deletion depends on host support; unmanaged and project-local deletion require a separate workflow.

## 0.3.0

- Made local-only initialization the default; GitHub synchronization is optional.
- Added a one-time cross-device setup question.
- Added Windows Task Scheduler registration and ZCode directory discovery.
- Excluded .git metadata from new imports.
- Added provenance records for self-created, third-party, modified, and unknown skills.
- Added persistent agent instruction guidance and concise catalog output.

## 0.2.0

- Added automatic catalog output after managed installation attempts.
- Added a catalog test to the isolated self-test suite.

## 0.1.0

- Added local scanning, duplicate detection, shared skill links, project isolation, optional Git synchronization, logical deletion and recovery, and initialization self-tests.

## Known limitations

- Native installation hooks and interactive deletion depend on the host agent.
- Cloud-folder synchronization and automatic migration of populated local libraries to GitHub are not implemented.
- Windows scheduling and the 0.3.x changes require further execution testing. Earlier isolated tests do not establish real cross-device or cloud-agent compatibility.
