# AgentGuard – manual test results

Draft for the "Notes for reviewers" section of the Pull Request.

## Setup

- Two small Flask + OpenAI "support assistant" apps with the same features (chat, RAG over uploaded documents, tools):
  - **App A** contains six planted issues, one per risk area.
  - **App B** implements the same features safely, with decoys (API key read from the environment, a `token_count` variable, `textContent`, a tenant filter taken from the session).
- Each app was reviewed by Claude Code (CLI 2.1.316) **with** and **without** the skill installed.
- Both apps were also reviewed with the skill by GitHub Copilot CLI 1.0.105 on Windows (Free plan; Copilot Fusion selected the model automatically and chose GPT-6 Luna).
- Both apps were also reviewed with the skill by Codex CLI 0.166.0 on Windows (GPT-6 Luna, default model). Codex's Windows sandbox could not start on this machine, so it ran with `--sandbox danger-full-access --ask-for-approval on-request`, and the prompt added "Do not modify any files."

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

### GitHub Copilot CLI (GPT-6 Luna), with the skill

| | App A | App B |
|---|---|---|
| Skill selected automatically | yes (`skill(security-agent-guard)`) | yes (loaded its references) |
| Planted issues found (of 6) | 5 of 6: prompt injection, agency and tool calling merged into one finding; RAG leak; admin key in prompt; `innerHTML`. Missed: full conversations written to the log. | n/a |
| Decoys reported as findings | n/a | 0 |
| Findings reported | 4 high | 1 high (the unplanned tenant-vs-user upload gap) |
| General issues kept separate | yes (SSRF under "Out of scope") | yes |
| Report format | used a 1-10 confidence score instead of confirmed/suspected, but did say "Confirmed" in the detailed finding | same |

On App B, Copilot offered to create `SECURITY-REVIEW.md` only after the follow-up option "Commit a summary of findings" was selected. The write was declined and the report was shown in chat.

### Codex CLI (GPT-6 Luna), with the skill

| | App A | App B |
|---|---|---|
| Skill selected automatically | yes ("I'll use the `security-agent-guard` skill"); read `SKILL.md`, then only the relevant references | yes |
| Planted issues found (of 6) | 6 of 6: prompt injection, agency and tool calling as one finding; RAG leak; admin key in prompt; `innerHTML`; full conversations logged | n/a |
| Decoys reported as findings | n/a | 0 (listed `textContent`, the step limit, the path check and the parameterized query as good controls) |
| Findings reported | 3 high, 2 medium | 1 low (tenant-wide document poisoning) |
| Report format | followed it: severity plus confirmed, file and line for each step, coverage, out of scope (SSRF, session key) | same |
| Files changed | none | none |

Both runs on App B found a real gap that was not planted: uploads are filtered by tenant but not by user, while the README and the prompt describe documents as the customer's own.

## What this shows

- **Detection:** on these small apps, Claude Code found the planted issues equally well without the skill. The skill did not add detections here.
- **Precision and focus:** with the skill, App B received one finding about the AI feature plus one low-severity note. Without it, it received five findings, including a medium finding that depended on login code that was not in the project.
- **Report quality:** with the skill, every finding had the source, prompt and sink locations, a certainty label and a coverage statement, and general web issues were listed separately.

## Limitations

- Only one or two runs per condition, so model output varies between runs. For example, the severity of the App B upload finding was "low" in an earlier run and "high" in this one.
- The test apps are small, and they were written by the skill's authors.
- Agents tested: Claude Code, GitHub Copilot CLI and Codex CLI (both on GPT-6 Luna). Not tested: Gemini CLI (the free API quota was used up), Cursor.
- On Windows, Codex's sandbox could not start, so its runs had no sandbox. They were read-only by instruction, not by enforcement.
