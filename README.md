# SkillHub

Automatically discover, collect, deduplicate, and synchronize skills across supported AI agents and devices through a unified skill library. Manage your skills with private GitHub backup, automated self-tests, and a visual skill directory.

## Install

Give your local AI agent this repository URL and ask it to install and initialize the `skill-manager` skill:

https://github.com/zhaoqingxia06/SkillHub

The agent should read `skill-manager/SKILL.md`, copy the complete skill directory (including scripts and tests) to its supported shared skill directory, and follow the initialization instructions. The user must approve local changes, any private repository upload, and optional scheduling. Use a separate private repository for personal skills; never use this public source repository as the personal library.

## Version 0.3.1 (preview)

See [installation and usage instructions](skill-manager/README.md) and [skill definition](skill-manager/SKILL.md). Python 3.9+; Git is required for remote synchronization. The automatic scheduler currently targets macOS. Native install hooks, real cross-device synchronization and cloud-agent integration require further validation; not all agents support these capabilities.


## V0.3 changes
Local-first initialization; GitHub is optional. Ask once whether cross-computer use is needed, configure a supplied and authorized destination only. Windows Task Scheduler registration added (requires real-device validation); macOS and Windows scheduled scans default to pending review. Existing Git metadata is excluded from import, not copied. Catalog includes provenance (self, third-party, modified, unknown); use `install PATH --approved --origin third-party --source-url URL` or `origin NAME self` for confirmed attribution. Existing skills without evidence remain unknown. Cloud-folder transport and migration of populated local libraries to GitHub are not implemented in this revision. Native install interception remains platform-dependent. V0.3 has not been executed in a real device environment yet.

### Compact management panel (0.3.1)
Global and project sections only, responsive compact grid, inline self-created labels and direct per-skill delete controls where the host supports verified actions. No summary metrics. Confirm deletion and refresh the real catalog after executing the existing managed-global delete command. Hosts without actionable UI use natural-language commands; project-local and unmanaged deletion require a separate verified workflow.
