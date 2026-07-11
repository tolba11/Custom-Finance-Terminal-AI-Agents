"""Deep Finance — multi-model chat engine (Anthropic + Perplexity)."""
import requests

from lib.config import (get_anthropic_key, get_perplexity_key,
                        get_perplexity_search_key)

MODELS = {
    "Claude Fable 5": {"provider": "anthropic", "id": "claude-fable-5",
                       "hint": "Most capable · premium cost"},
    "Claude Opus 4.8": {"provider": "anthropic", "id": "claude-opus-4-8",
                        "hint": "Deep reasoning · high cost"},
    "Claude Sonnet 5": {"provider": "anthropic", "id": "claude-sonnet-5",
                        "hint": "Fast + strong · moderate cost"},
    "Perplexity Sonar Pro": {"provider": "perplexity", "id": "sonar-pro",
                             "hint": "Live web + citations"},
    "Perplexity Sonar": {"provider": "perplexity", "id": "sonar",
                         "hint": "Live web · cheapest"},
}

SYSTEM = (
    "You are Deep Finance, the research copilot inside Tolba Terminal, a "
    "personal markets dashboard. Answer with the rigor of a sell-side "
    "analyst: concrete numbers, clear structure, cite sources when you "
    "have them. You provide analysis and information, not personalized "
    "investment advice; note that where relevant. Markdown formatting.")


def anthropic_ready():
    return bool(get_anthropic_key())


def perplexity_ready():
    return bool(get_perplexity_key())


def chat_anthropic(model_id, messages, context="", blocks=None,
                   file_text=""):
    """messages: [{'role','content'}...]. blocks are Claude-native
    attachment blocks (images/PDFs) for the latest user turn.
    Returns (text, error)."""
    import anthropic
    client = anthropic.Anthropic(api_key=get_anthropic_key())
    system = SYSTEM + (f"\n\nLive web context gathered for this query:\n"
                       f"{context}" if context else "")
    msgs = [dict(m) for m in messages[-16:]]
    if msgs and (blocks or file_text):
        last = msgs[-1]
        text = last["content"]
        if file_text:
            text = f"{text}\n\nATTACHED FILE CONTENTS:\n{file_text}"
        last["content"] = (blocks or []) + [{"type": "text", "text": text}]
    try:
        r = client.messages.create(
            model=model_id, max_tokens=2000, system=system,
            messages=msgs)
        return "".join(b.text for b in r.content if b.type == "text"), ""
    except Exception as e:
        return "", f"{type(e).__name__}: {e}"


def chat_perplexity(model_id, messages, file_text=""):
    """Returns (text, citations list, error)."""
    messages = [dict(m) for m in messages]
    if messages and file_text:
        messages[-1]["content"] += (f"\n\nATTACHED FILE CONTENTS:\n"
                                    f"{file_text}")
    try:
        r = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {get_perplexity_key()}",
                     "Content-Type": "application/json"},
            json={"model": model_id,
                  "messages": ([{"role": "system", "content": SYSTEM}]
                               + messages[-16:])},
            timeout=90)
        data = r.json()
        if r.status_code != 200:
            err = (data.get("error", {}) or {}).get("message",
                                                    f"HTTP {r.status_code}")
            return "", [], str(err)[:300]
        text = data["choices"][0]["message"]["content"]
        cites = data.get("citations") or [
            s.get("url", "") for s in data.get("search_results", [])]
        return text, [c for c in cites if c], ""
    except Exception as e:
        return "", [], f"{type(e).__name__}: {e}"


def web_ground(query):
    """Optional: Perplexity Search API results to ground Claude answers.
    Returns snippet text ('' if unavailable) — never raises."""
    try:
        r = requests.post(
            "https://api.perplexity.ai/search",
            headers={"Authorization":
                     f"Bearer {get_perplexity_search_key()}",
                     "Content-Type": "application/json"},
            json={"query": query, "max_results": 5}, timeout=20)
        if r.status_code != 200:
            return ""
        results = r.json().get("results", [])
        return "\n".join(
            f"- {x.get('title', '')}: {x.get('snippet', '')[:220]} "
            f"({x.get('url', '')})" for x in results[:5])
    except Exception:
        return ""
