---
agent: "agent"
description: "Inspect a given file and its recent edits before executing the requested operation."
---

Please follow these steps exactly:

1. You are given:
   - a file path or file content (`file_path`, `file_content`)
   - the user’s intended follow-up operation (`task_description`)

2. First, open and read the provided file fully.
   - If a diff/patch is also provided, analyze it to identify which lines/sections were modified.
   - If no explicit diff is given, infer likely changed areas from the latest available context or from the user’s direct message about edits.

3. Summarize:
   - current file purpose
   - detected modifications and which parts changed
   - any potential implications for the requested operation

4. Only after confirming the above, perform the requested operation (`task_description`) on the file content.

Output:
- Step 1: file review summary
- Step 2: changed-region analysis
- Step 3: result of the requested operation

Use clear, concise language and keep each stage separated.

Inputs:
- `file_path` (optional)
- `file_content` (optional)
- `diff` or `patch` (optional)
- `task_description` (required)
