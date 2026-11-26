---
name: skill-manager
description: Manage a personal cross-device Agent Skill library. Use for installing, importing, listing, deduplicating, syncing, disabling, deleting, restoring, or testing skills, and initializing a new local Agent environment. Invoke before and after any skill installation you control.
---
# Skill Manager v0.2

Use the bundled `scripts/manager.py` (Python 3.9+). All paths are relative to this skill's folder unless absolute. Do not claim a command ran without actual tool output. Never execute scripts contained in imported skills during import or self-test.

## Setup (first use)
1. Determine whether the Agent has access to the user's real local filesystem and shell. A cloud sandbox is not the user's computer. If remote-only, offer the cloud workflow below.
2. Ask for or reuse the user's own dedicated private GitHub repository, not the author's repository. Confirm private status through an authorized GitHub tool or the user; do not create public repos. Use existing Git credentials, never ask for tokens in chat. Obtain permission for bulk import and optional scheduling; inspect skills for confidential work material before approval. Project skills remain local in V1.
3. Run `python3 scripts/manager.py setup --remote <private-repo-url> --confirm-private --approve-import --schedule` only after those approvals. Omit remote flags for local-only mode, omit approval for preview, omit schedule if not authorized. Add `--adapter <verified-global-skill-directory>` for other Agents and `--project <project-root>` for project inventory. Do not assume any unverified directory is an Agent skill root. Default shared directory is `~/.agents/skills/`. Existing candidate roots are checked conservatively; custom roots require explicit confirmation. Setup runs isolated self-tests automatically. Report failures separately from unavailable integrations.
4. Explain that shared directory readers discover the same files; symlinks require platform support and may require Agent refresh. Backups are retained outside active roots when original files are replaced by links. Do not delete backups automatically.

## Install a Skill
For every install request handled by the Agent, invoke this manager first. Check `list` and inspect existing record by name and source/content, then obtain the actual skill package using trusted tooling into a temporary local directory. Inspect its instructions, scripts, dependencies, licensing and sensitive content. Get explicit approval before importing/uploading. Run `python3 scripts/manager.py install <path-to-skill-folder> --approved`. It logs precheck and postcheck, does not overwrite conflicting names, and syncs if configured. If the folder is for a project, do not install it as global; keep it under the project and inventory it with `setup --project ...`. Verify that the Agent actually discovers and can use the skill. Do not treat a pending/conflict result as installed. Native UI installs and third-party CLIs may bypass this Skill; no universal hook exists. Periodic scanning is a fallback, not proof of pre-install interception.

## Manage
- `python3 scripts/manager.py list`: list records and configured directories. Timestamps are first-seen, not original creation dates. Usage counts are unknown.
- `python3 scripts/manager.py sync`: pull, detect unapproved local folders, expose active skills, push. `--approve-import` imports all scanned eligible folders; only use after reviewing and getting approval. It may also adopt matching physical folders into links, preserving backups.
- `python3 scripts/manager.py disable NAME` / `delete NAME` / `restore NAME`: explicitly authorized actions; logical deletion retains contents and tombstone. Unmanaged original copies are not deleted.
- `python3 scripts/manager.py test`: isolated self-tests. Report actual pass/fail and unverified real environments. For actual environment verification, inspect configured paths, Git status, scheduler logs, and ask each Agent to invoke a harmless test skill using its native interface. A simulated test never counts as real Agent verification.
- To update a conflicting skill, review both versions and reconcile manually; automatic overwrite is intentionally disabled in V1.

## Cloud-only workflow
Do not run local setup in a cloud sandbox and claim it changes the user's machine. If an authorized connector permits reading the user's private GitHub repo, read `records/*.json` and active `skills/<name>/SKILL.md`, inspect dependencies and resources before using instructions. Dynamic reading is not native installation or automatic discovery. If connector access is unavailable, request a standard export/import package. Do not claim automatic management of the platform's installed skills unless a verified official interface actually supports it. Never call unauthorized private APIs or automate credentials.

## Output
Summarize discovered paths, actions, blockers, and verified results. Never upload confidential project content or credentials. Never imply all tools were connected when only file access was tested.

## Mandatory post-install catalog
After every installation attempt handled by the Manager (including duplicate, conflict or failed attempts), display the latest full catalog to the user, not just a success message. Use the actual `catalog` object returned by the command or run `python3 scripts/manager.py catalog` if needed. Show total, active and newly collected counts; group names by global/project and project name, show inactive/unmanaged entries separately or label their status, and mark only actual new entries as NEW. Use compact columns, a table or native visual components when available; otherwise use compact Markdown. Do not invent names, counts, times or discovery results. Explain that the catalog covers the managed library and configured local roots, not inaccessible cloud accounts. For remote-only execution use authorized repository records and label scope limitations. If the installation failed, retain the error and show the existing catalog only if readable. Scheduled scans cannot force a visible message into an unrelated Agent conversation.
