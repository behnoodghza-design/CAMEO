# Agent Memory Rule

1. BEFORE any structural or architectural edit:
   - Load [agent_memory/project_structure.json](cci:7://file:///c:/Users/aminh/OneDrive/Desktop/CAMEO/CAMEO/agent_memory/project_structure.json:0:0-0:0).
   - Review [agent_memory/README.md](cci:7://file:///c:/Users/aminh/OneDrive/Desktop/CAMEO/CAMEO/agent_memory/README.md:0:0-0:0).
   - Abort the edit if these files are unreadable.

2. AFTER every structural change (new files, API routes, schema updates, major refactors):
   - Append a dated entry to `agent_memory/history/<YYYY-MM-DD>.md` summarizing:
     - Files touched
     - Nature of the change
     - Reason/impact
   - Update [agent_memory/project_structure.json](cci:7://file:///c:/Users/aminh/OneDrive/Desktop/CAMEO/CAMEO/agent_memory/project_structure.json:0:0-0:0) if architecture, endpoints, or critical files changed.
   - Update [agent_memory/README.md](cci:7://file:///c:/Users/aminh/OneDrive/Desktop/CAMEO/CAMEO/agent_memory/README.md:0:0-0:0) if project context or guidelines changed.

3. NEVER skip the memory read/write steps for major edits. If unsure whether a change is “structural,” treat it as structural.

4. If memory files become inconsistent or corrupted:
   - Halt further edits.
   - Notify the user with a recommended remediation plan.