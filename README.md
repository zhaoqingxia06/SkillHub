# SkillHub

Automatically discover, collect, deduplicate, and synchronize skills across supported AI agents and devices through a unified skill library. Manage your skills with private GitHub backup, automated self-tests, and a visual skill directory.

## Install

Give your local AI agent this repository URL and ask it to install and initialize the `skill-manager` skill:

https://github.com/zhaoqingxia06/SkillHub

The agent should read `skill-manager/SKILL.md`, copy the complete skill directory (including scripts and tests) to its supported shared skill directory, and follow the initialization instructions. The user must approve local changes, any private repository upload, and optional scheduling. Use a separate private repository for personal skills; never use this public source repository as the personal library.

## Version 0.2 (preview)

See [installation and usage instructions](skill-manager/README.md) and [skill definition](skill-manager/SKILL.md). Python 3.9+; Git is required for remote synchronization. The automatic scheduler currently targets macOS. Native install hooks, real cross-device synchronization and cloud-agent integration require further validation; not all agents support these capabilities.
