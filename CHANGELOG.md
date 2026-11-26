# Changelog

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
