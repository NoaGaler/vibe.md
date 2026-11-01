# Status – where we stopped

## Done
- Skill written and pushed: branch `add-security-agent-guard` (validator OK, 213 tests OK).
- Tested with Claude Code, with and without the skill: see `test-results.md` and `reports/`.
  ra = app 1 with skill, rb = app 2 with skill, rc = app 1 without, rd = app 2 without.
- Maintainer (NirGeron98) approved the idea on issue #20 and closed it; next step is the PR.
- On the user's computer: Gemini CLI installed with an API key, skill installed into both test apps.

## Next
1. On an unrestricted network: run Gemini on acme-support-1 and acme-support-2, save the answers.
2. Install Codex (download the Windows .exe or `npm install -g @openai/codex`), install the skill with `--agent codex`, run both apps.
3. Compare the answers with `EXPECTED.md` and update `test-results.md`.
4. Open the PR from `add-security-agent-guard`, link it on issue #20.

Note: `EXPECTED.md` contains the answers, so keep it out of the folders the agents review.
