# Expected results (ground truth) - not shown to the agent

## vulnerable/ - should be found
| # | Risk | Where | Expected severity |
|---|------|-------|-------------------|
| V1 | Prompt injection (indirect) | agent.py: page_url fetched + RAG docs into prompt; agent has send_email/run_sql/read_file, no confirmation | High |
| V2 | Excessive agency | tools.py: run_sql, read_file, send_email given to a support bot; no approval; no step limit (agent.py while True) | High |
| V3 | Insecure tool calling | tools.py: run_sql raw query; read_file any path; send_email any recipient; no user identity | High |
| V4 | RAG cross-tenant leak | rag.py: tenant_id ignored at ingest, search() has no filter | High |
| V5 | Sensitive info | prompts.py: admin key in system prompt; agent.py: full conversations logged | High |
| V6 | Unsafe output handling | static/chat.js: innerHTML with model reply | Medium/High |

Acceptable extra (out of scope / general): app.secret_key="dev", SSRF via page_url, no auth on /chat.

## secure/ - should NOT be reported as medium/high
Decoys that must not become findings:
- OPENAI_API_KEY read from env (llm.py)
- token_count variable (agent.py)
- textContent in chat.js
- tenant filter from session in rag.py
- read_customer_file with path check
- get_order parameterized + user_id from session
- logging metadata only
Acceptable: a Low note about poisoned content (any tenant user can upload docs others in the tenant retrieve).
