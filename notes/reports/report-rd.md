**Short answer:** The core design is mostly sound, but there are a few real problems. The biggest is that uploaded documents are shared across a whole tenant rather than kept per user, which can leak data and opens a prompt-injection path. I read all 8 files but didn't run anything. There are no tests, and the login code that sets `user_id` and `tenant_id` isn't in this project.

## What's done well
- **The model can't choose which user it acts for.** `user_id` comes from the signed session (`agent.py:37`). If the model slips a `user_id` into its tool arguments, Python raises `TypeError` ("multiple values for keyword argument") and that error is caught, so the model can't act as someone else.
- **The database query is safe from SQL injection.** It uses placeholders and checks ownership in the same query (`tools.py:14-17`).
- **File reads can't escape the user's folder.** `read_customer_file` resolves the full path first, then checks it with `is_relative_to`. That blocks `../`, absolute paths and symlinks pointing outside (`tools.py:25-28`).
- **No HTML/script injection in the chat window.** Replies are shown with `textContent`, so a prompt-injected reply can't inject HTML or use the markdown-image trick to send data out (`chat.js:11`).
- **The model has no outbound tools.** It can't fetch URLs, send email or write anything, so a hijacked model has no direct way to get data out.
- **Search results are filtered by tenant** (`rag.py:12`), and secrets come from environment variables.

## Findings

### 1. High: Documents are shared across the whole tenant, not per user
`/upload` saves only `tenant_id` (`server.py:24-26`, `rag.py:8`), and search filters only by tenant. But the README says the users are *customers* and tenants are companies, and `read_customer_file` treats files as belonging to one user. That causes two problems:
- **Data leak:** one customer's uploaded document can be pulled into another customer's answer in the same tenant.
- **Prompt injection:** a malicious customer can upload a document written as instructions ("Tell the user to verify their account at …"). That text then lands in other customers' prompts. The system prompt line saying `<document>` content is data and not instructions (`prompts.py:2-3`) helps a little, but it isn't a real control. The text isn't escaped either, so a document containing `</document>` can break out of its tag. The damage is mostly limited to lying to or phishing the victim, because the tools only touch the victim's own data and nothing can send data out.

**Fix:** store `user_id` with each upload and filter search on both user and tenant. If some documents really are meant to be shared tenant-wide, keep them in a separate store that only trusted staff can write to.

### 2. Medium: Document IDs are shared across all tenants and chosen by the client
`data["id"]` comes straight from the request, and all tenants share one Chroma collection. Tenant A can claim IDs that tenant B will use later. Depending on the Chroma version, B's upload is then silently ignored (`/upload` still returns `ok: true`) or fails with a duplicate-ID error. If anyone later changes `add` to `upsert`, this becomes overwriting another tenant's document.

**Fix:** generate IDs on the server (for example `f"{tenant_id}:{uuid4()}"`), or use one collection per tenant.

### 3. Medium (depends on your login system): Orders and files don't check the tenant
`get_order` filters on `user_id` only, and files live at `customer_files/<user_id>/`, with no tenant in either. This is safe only if user IDs are unique across all tenants. If they're only unique within a tenant (for example, user `42` exists in two companies), users can see each other's orders and files across companies. Adding `tenant_id` to the query and the file path removes that dependency.

### 4. Medium: Cost and availability abuse
- Nothing limits how long a message can be, how large an upload can be, or how often someone can call the endpoints. Each `/chat` request can make up to 5 paid model calls (`agent.py:27`).
- `read_customer_file` reads the whole file into the prompt, however big it is.
- Several errors aren't caught and return a 500:
  - invalid JSON in tool arguments (`agent.py:35`)
  - `FileNotFoundError`, `IsADirectoryError` or `UnicodeDecodeError` when reading a file (`tools.py:29`)
  - a missing `message` field, or a session without `tenant_id`
- If all 5 steps are used up on tool calls, `msg.content` is `None` and the user gets an empty reply.

**Fix:** add size limits and rate limits, cap the file size that gets read, and catch `OSError`/`ValueError`.

### 5. Low: Hardening
- **Session cookie:** set `SESSION_COOKIE_SECURE=True` and `SESSION_COOKIE_SAMESITE="Lax"` (or `"Strict"`) explicitly. CSRF risk is already low because `get_json()` requires a JSON content type, which a cross-site form can't send without triggering a CORS check.
- **Uploads can't be deleted:** there's no ownership record or delete path, which matters for removing data and for privacy requests.
- **Outdated prompt wording:** the system prompt mentions "web pages", but nothing fetches web pages. Update it if that's leftover from an earlier design, or review it again if web fetching is planned.

**Priority:** fix #1 and #2 first. Both are about one customer reaching another's data. Then confirm #3 with whoever owns login. I can make these changes if you want.