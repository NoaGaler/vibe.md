import json
import logging
import requests

from .llm import client, MODEL
from .prompts import SYSTEM_PROMPT
from .rag import search
from .tools import TOOLS

log = logging.getLogger("assistant")
logging.basicConfig(filename="conversations.log", level=logging.INFO)

TOOL_SPECS = [
    {"type": "function", "function": {"name": name, "parameters": {"type": "object"}}}
    for name in TOOLS
]


def answer(user_message: str, page_url: str | None = None):
    context = "\n".join(search(user_message))
    if page_url:
        context += "\n" + requests.get(page_url, timeout=10).text

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_message}"},
    ]
    while True:
        reply = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOL_SPECS)
        msg = reply.choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            break
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            result = TOOLS[call.function.name](**args)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})

    log.info("user=%s prompt=%s reply=%s", user_message, messages, msg.content)
    return msg.content
