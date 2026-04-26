---
agent: "agent"
description: "Review a target file, compare it against prior understanding, then execute the requested edit operation."
---

Please follow these steps exactly:

1. You are given:
   - a file path or file content (`file_path`, `file_content`)
   - optional prior understanding of the same file (`previous_understanding`)
   - optional change signals (`diff`, `patch`, `user_edit_notes`)
   - the user’s requested modification (`task_description`)

2. Phase 1 - Inspect and summarize the specified file.
   - Open and read the provided file fully before doing any edits.
   - Summarize the file’s current purpose, structure, and key sections.
   - If there are obvious recent edits in the file, call them out briefly.

3. Phase 2 - Compare the file with your prior understanding.
   - Use `previous_understanding` when available.
   - If `diff`, `patch`, or `user_edit_notes` are provided, use them as evidence.
   - Identify the gap between current file reality and your prior understanding.
   - Explicitly list what is new, changed, removed, or still uncertain.
   - Explain how those gaps affect the requested modification.

4. Phase 3 - Execute the requested modification.
   - Only after completing Phase 1 and Phase 2, perform `task_description`.
   - Apply changes consistent with the file’s current state and detected gaps.
   - Avoid assumptions that conflict with the latest file content.

Output:

- Phase 1: file inspection summary
- Phase 2: prior-understanding gap analysis
- Phase 3: requested modification result

Use clear, concise language and keep each stage separated.

Inputs:

- `file_path` (optional)
- `file_content` (optional)
- `previous_understanding` (optional)
- `diff` or `patch` (optional)
- `user_edit_notes` (optional)
- `task_description` (required)
