# Codex execution environment

Read this before writing files or calling network tools. The active Codex
session's permissions, sandbox, network policy and approval rules are authoritative.
Do not assume any host is reachable, home directories writable, or temporary
directories forbidden. Use only permitted paths. Request an approved escalation
when required; never bypass a restriction using another tool.

Keep scratch files and run artifacts untracked. Inspect all existing changes;
do not dismiss unfamiliar files as sandbox artifacts or discard user work.
Use explicit paths for staging, and explicit branch names for pushes. Upstream
tracking availability depends on the session, not on this plugin. Never force
push except with --force-with-lease after an authorized history rewrite.

Use available web search/page retrieval or a configured documentation MCP for
external documentation. If unavailable, report the missing capability rather
than pretending research succeeded. MCP configuration and authentication belong
to the consuming project/user; this package needs no bundled MCP servers.

The orchestrator and every delegated file-writing or network-calling role must
read this policy. User authorization and host instructions take precedence over
workflow confirmation defaults; do not ask again for actions already authorized.

## 1. Filesystem reads
Follow the active session's read permissions.
## 2. Filesystem writes
Use the working tree and permitted scratch locations only.
## 3. Network
Follow actual network policy; prefer available documentation tools.
## 4. Existing changes
Treat unfamiliar files as user work until inspected; never ignore by filename.
## 5. Pushes
Name the branch explicitly. No fixed claim about upstream tracking is made.
## 6. Readers
The orchestrator and all delegated roles read this document before execution.
