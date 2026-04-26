---
description: "Review all provided reference files first, then write or modify the target file's code"
agent: "agent"
argument-hint: "reference files, target file, and edit task"
---

Follow these steps exactly:

1. You will receive:
   - One or more reference files or reference contents (`reference_file_paths`, `reference_file_contents`)
   - Optional prior understanding of the same file (`previous_understanding`)
   - Optional change signals (`diff`, `patch`, `user_edit_notes`)
   - The target file or target content (`file_path`, `file_content`)
   - The user's requested modification (`task_description`)

2. Phase 1 - Review all reference files first.
   - Before touching any target file, read every reference file provided by the user.
   - Briefly summarize each reference file's purpose, structure, and the points most relevant to the task.
   - If the reference files share naming, structure, flow, or implementation patterns, extract reusable patterns from them.

3. Phase 2 - Review the specified reference files to confirm your understanding of the target instructions.
   - Review the provided reference files again to better verify what the target task expects.
   - Use the reference files to sharpen your understanding before comparing the target file with `previous_understanding`.
   - Read the target file's current content and compare it with `previous_understanding`.
   - If `diff`, `patch`, or `user_edit_notes` are provided, use them as evidence of recent changes.
   - Explicitly list the gaps between the current target file and the prior understanding: what is new, changed, removed, or still uncertain.
   - Explain how those gaps affect the upcoming edit.

4. Phase 3 - Write the target file based on the reference files.
   - Only after completing Phase 1 and Phase 2 should you modify the target file.
   - Prefer the structure, naming, style, and approach used in the reference files unless `task_description` explicitly requires something different.
   - Avoid assumptions that conflict with the latest target file content or the reference file content.
   - If the reference files conflict with each other, choose the approach that best fits the task and the current target file context, and briefly explain the tradeoff in your output.

Output format:

- Phase 1: Reference file inspection summary
- Phase 2: Gap analysis between the target file and prior understanding
- Phase 3: Completed modification based on the reference files

Keep the tone clear and concise, and present each phase separately.

Inputs:

- `reference_file_paths` or `reference_file_contents` (required, at least one)
- `file_path` or `file_content` (required, target file)
- `previous_understanding` (optional)
- `diff` / `patch` / `user_edit_notes` (optional)
- `task_description` (required)
