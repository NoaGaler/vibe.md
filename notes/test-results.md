# AgentGuard – manual test results

Draft for the "Notes for reviewers" section of the Pull Request.

## Setup

- Two small Flask + OpenAI "support assistant" apps with the same features (chat, RAG over uploaded documents, tools):
  - **App A** contains six planted issues, one per risk area.
  - **App B** implements the same features safely, with decoys (API key read from the environment, a `token_count` variable, `textContent`, a tenant filter taken from the session).
- Each app was reviewed by Claude Code (CLI 2.1.316) **with** and **without** the skill installed.
- Same prompt in all runs, without naming the skill: *"Is the AI support assistant in this project secure? Please review the whole project."*
- Read-only tools only. One run per condition, in neutrally named folders.

## Results

| | App A with skill | App A without | App B with skill | App B without |
|---|---|---|---|---|
| Skill selected automatically | yes | n/a | yes | n/a |
| Planted issues found (of 6) | 6 | 6 | n/a | n/a |
| Decoys reported as findings | n/a | n/a | 0 | 0 |
| Findings reported (high / medium / low) | 7 / 2 / 0 | 8 / 4 / 0 (general web issues mixed in) | 1 / 0 / 1 | 1 / 3 / 1 |
| AI risks separated from general web issues | yes ("Out of scope") | no | yes | no |
| Confirmed vs. suspected marked | yes | no | yes | no |
| Coverage statement | yes | no | yes | no |

Both runs on App B found a real gap that was not planted: uploads are filtered by tenant but not by user, while the README and the prompt describe documents as the customer's own.

## What this shows

- **Detection:** on these small apps, Claude Code found the planted issues equally well without the skill. The skill did not add detections here.
- **Precision and focus:** with the skill, App B received one finding about the AI feature plus one low-severity note. Without it, it received five findings, including a medium finding that depended on login code that was not in the project.
- **Report quality:** with the skill, every finding had the source, prompt and sink locations, a certainty label and a coverage statement, and general web issues were listed separately.

## Limitations

- Only one or two runs per condition, so model output varies between runs. For example, the severity of the App B upload finding was "low" in an earlier run and "high" in this one.
- The test apps are small, and they were written by the skill's authors.
- Only one agent was tested (Claude Code). Codex, Cursor, Gemini CLI and Copilot were not tested.
