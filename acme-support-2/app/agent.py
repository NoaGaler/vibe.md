import json
import logging

from .llm import client, MODEL
from .prompts import SYSTEM_PROMPT
from .rag import search
from .tools import TOOLS, ToolError

log = logging.getLogger("assistant")
MAX_STEPS = 5

TOOL_SPECS = [
    {"type": "function", "function": {"name": "get_order", "parameters": {
        "type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}}},
    {"type": "function", "function": {"name": "read_customer_file", "parameters": {
        "type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}},
]


def answer(user_id: str, tenant_id: str, user_message: str):
    context = "\n".join(f"<document>{d}</document>" for d in search(user_message, tenant_id))
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{context}\n\nQuestion: {user_message}"},
    ]
    token_count = 0
    for _ in range(MAX_STEPS):
        reply = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOL_SPECS)
        token_count += reply.usage.total_tokens
        msg = reply.choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            break
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            try:
                result = TOOLS[call.function.name](user_id=user_id, **args)
            except (ToolError, TypeError, KeyError) as error:
                result = f"error: {error}"
            messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})

    log.info("tenant=%s steps=%d tokens=%d", tenant_id, len(messages), token_count)
    return msg.content
