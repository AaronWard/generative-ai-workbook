#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LM Studio + gpt-oss-20b THINKING + FINAL extractor (robust).

Order of attempts per prompt:
  1) /v1/chat/completions with native reasoning enabled:
       - reads choices[0].message.reasoning (LM Studio 0.3.23+)
       - or choices[0].message.reasoning_content (older dev builds)
       - strips <think>...</think> from content if present
  2) If no reasoning found: force strict JSON with required fields
       {"thinking": "...", "final": "..."} via response_format:json_schema
  3) If still missing: fallback to Harmony tags (<|channel|>analysis/final)

CLI:
  python lmstudio_gptoss.py --high "Prove the quadratic formula"
  python lmstudio_gptoss.py --low "Why did Thomas doubt Jesus?"

Env:
  LMSTUDIO_URL (default http://127.0.0.1:1234)
"""

import argparse, json, os, re, sys, urllib.request, urllib.error

LMSTUDIO_URL_DEFAULT = os.environ.get("LMSTUDIO_URL", "http://127.0.0.1:1234")

# -------------------------
# HTTP helper
# -------------------------
def http_post_json(url, payload, timeout=180):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return json.loads(raw), raw, None
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        return None, raw, f"HTTP {e.code}"
    except Exception as e:
        return None, None, f"{type(e).__name__}: {e}"

# -------------------------
# Reasoning extraction (chat)
# -------------------------
THINK_TAG_RE = re.compile(r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE)

def extract_reasoning_from_message(msg):
    # Preferred (LM Studio 0.3.23+)
    val = msg.get("reasoning")
    if isinstance(val, str) and val.strip():
        return val.strip(), "message.reasoning"

    # Older dev toggle / variants
    val = msg.get("reasoning_content")
    if isinstance(val, str) and val.strip():
        return val.strip(), "message.reasoning_content"

    # Embedded tags (last resort within this call)
    content = (msg.get("content") or "")
    m = THINK_TAG_RE.search(content)
    if m:
        return m.group(1).strip(), "content.<think>"
    return None, None

def strip_think_tags(text):
    return THINK_TAG_RE.sub("", text).strip()

# -------------------------
# Harmony parsing fallback
# -------------------------
def parse_harmony_text(text):
    analysis = None
    final = None

    m_a = re.search(r"<\|channel\|>analysis<\|message\|>(.*?)(?:<\|end\|>|<\|channel\|>final)", text, flags=re.DOTALL)
    if m_a:
        analysis = m_a.group(1).strip()
    m_f = re.search(r"<\|channel\|>final<\|message\|>(.*)", text, flags=re.DOTALL)
    if m_f:
        final = m_f.group(1).strip()

    if analysis is None:
        m = re.search(r"<\|analysis\|>(.*?)(?:<\|final\|>|$)", text, flags=re.DOTALL)
        if m:
            analysis = m.group(1).strip()
    if final is None:
        m = re.search(r"<\|final\|>(.*)", text, flags=re.DOTALL)
        if m:
            final = m.group(1).strip()

    if final is None and not re.search(r"<\|.*?\|>", text):
        final = text.strip()

    return analysis, final

# -------------------------
# Effort controls
# -------------------------
def token_budget_for_effort(effort):
    return {"low": 1024, "medium": 2048, "high": 4096}.get(effort, 2048)

def effort_value(effort):
    # Use OpenAI-style field recognized by some LM Studio builds.
    return effort if effort in ("low","medium","high") else "medium"

# -------------------------
# Call 1: chat.completions asking for native reasoning
# -------------------------
def call_chat_with_reasoning(server, model, effort, user_text, temperature, max_tokens, debug=False):
    payload = {
        "model": model,
        "messages": [
            {"role":"system","content":"Return the user-facing answer in content. Also include hidden reasoning if supported."},
            {"role":"user","content": user_text.strip()}
        ],
        "temperature": temperature,
        "top_p": 1.0,
        "max_tokens": max_tokens,

        # Ask for reasoning the way OpenAI reasoning models expect.
        "reasoning": {"effort": effort_value(effort)},

        # Hints some forks honor:
        "include_reasoning": True,
        "return_reasoning": True
    }
    url = f"{server.rstrip('/')}/v1/chat/completions"
    resp, raw, err = http_post_json(url, payload)
    if debug:
        sys.stderr.write(f"[debug] chat.completions err={err}\n")
        if raw: sys.stderr.write(f"[debug] raw(first 800): {raw[:800]}\n")

    if not resp or "choices" not in resp or not resp["choices"]:
        return None, None, {"path":"chat","reason":f"no choices ({err})"}

    msg = (resp["choices"][0].get("message") or {})
    reasoning, src = extract_reasoning_from_message(msg)
    final = strip_think_tags(msg.get("content") or "")

    meta = {"path":"chat","reason":src or "(no reasoning field)"}
    return reasoning, final, meta

# -------------------------
# Call 2: force strict JSON with required fields
# -------------------------
def call_chat_force_json(server, model, effort, user_text, temperature, max_tokens, debug=False):
    sys_msg = (
        "You must output ONLY a valid JSON object matching this exact schema. "
        "Schema: {\"thinking\":\"string\",\"final\":\"string\"}. "
        "Both fields are REQUIRED. Do NOT include any extra keys, text, or formatting."
    )
    payload = {
        "model": model,
        "temperature": temperature,
        "top_p": 1.0,
        "max_tokens": max_tokens,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "ThinkingFinal",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "thinking": {"type":"string"},
                        "final":    {"type":"string"}
                    },
                    "required": ["thinking","final"],
                    "additionalProperties": False
                }
            }
        },
        "messages": [
            {"role":"system","content": sys_msg},
            {"role":"user","content": user_text.strip()}
        ]
    }
    url = f"{server.rstrip('/')}/v1/chat/completions"
    resp, raw, err = http_post_json(url, payload)
    if debug:
        sys.stderr.write(f"[debug] chat.force-json err={err}\n")
        if raw: sys.stderr.write(f"[debug] raw(first 800): {raw[:800]}\n")

    if not resp or "choices" not in resp or not resp["choices"]:
        return None, None, {"path":"json","reason":f"no choices ({err})"}

    content = (resp["choices"][0].get("message") or {}).get("content") or ""
    try:
        obj = json.loads(content)
        thinking = (obj.get("thinking") or "").strip()
        final = (obj.get("final") or "").strip()
        if thinking and final:
            return thinking, final, {"path":"json","reason":"schema"}
    except Exception:
        pass
    return None, None, {"path":"json","reason":"parse-failed"}

# -------------------------
# Call 3: Harmony fallback
# -------------------------
HARMONY_SEED = """<|start|>system<|message|>
{system}
<|end|><|start|>user<|message|>
{user}
<|end|><|start|>assistant<|channel|>analysis<|message|>
"""

def call_harmony(server, model, effort, user_text, temperature, max_tokens, debug=False):
    system = f"Reasoning effort: {effort}. Use Harmony channels. Provide analysis in <|channel|>analysis and the user-facing answer in <|channel|>final."
    prompt = HARMONY_SEED.format(system=system, user=user_text.strip())
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "top_p": 1.0,
        "max_tokens": max_tokens
    }
    url = f"{server.rstrip('/')}/v1/completions"
    resp, raw, err = http_post_json(url, payload)
    if debug:
        sys.stderr.write(f"[debug] completions(Harmony) err={err}\n")
        if raw: sys.stderr.write(f"[debug] raw(first 800): {raw[:800]}\n")

    if not resp or "choices" not in resp or not resp["choices"]:
        return None, None, {"path":"harmony","reason":f"no choices ({err})"}

    text = (resp["choices"][0].get("text") or "").strip()
    a, f = parse_harmony_text(text)
    return a, f, {"path":"harmony","reason":"parsed-tags"}

# -------------------------
# CLI
# -------------------------
def main():
    p = argparse.ArgumentParser(description="LM Studio + gpt-oss-20b: print THINKING + FINAL cleanly.")
    p.add_argument("question", help="User prompt")
    p.add_argument("--server", default=LMSTUDIO_URL_DEFAULT, help="LM Studio base URL (default http://127.0.0.1:1234)")
    p.add_argument("--model", default="openai/gpt-oss-20b")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--low", action="store_true")
    g.add_argument("--medium", action="store_true")
    g.add_argument("--high", action="store_true")
    p.add_argument("--temp", type=float, default=0.2)
    p.add_argument("--max-tokens", type=int, default=None)
    p.add_argument("--chat-only", action="store_true", help="Skip Harmony fallback")
    p.add_argument("--harmony-only", action="store_true", help="Force Harmony only")
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()

    effort = "medium"
    if args.low: effort = "low"
    if args.high: effort = "high"

    max_tokens = args.max_tokens or token_budget_for_effort(effort)

    analysis = None
    final = None
    meta = {"path":"", "reason":""}

    # 1) Native reasoning via chat.completions
    if not args.harmony_only:
        a1, f1, m1 = call_chat_with_reasoning(args.server, args.model, effort, args.question, args.temp, max_tokens, args.debug)
        analysis = a1
        final = f1
        meta = m1

        # 2) If no reasoning, force JSON with required fields
        if (not analysis) or (not final):
            a2, f2, m2 = call_chat_force_json(args.server, args.model, effort, args.question, args.temp, max_tokens, args.debug)
            if a2 and not analysis:
                analysis = a2
                meta = m2
            if f2 and not final:
                final = f2
                meta = m2

    # 3) Harmony fallback if still missing and allowed
    if ((not analysis) or (not final)) and not args.chat_only:
        a3, f3, m3 = call_harmony(args.server, args.model, effort, args.question, args.temp, max_tokens, args.debug)
        if a3 and not analysis:
            analysis = a3
            meta = m3
        if f3 and not final:
            final = f3
            meta = m3

    # ---- Print both parts ----
    print("=== THINKING (hidden) ===")
    if analysis and analysis.strip():
        print(analysis.strip(), end="\n\n")
    else:
        print("(no reasoning returned by server)\n")

    print("=== FINAL ANSWER ===")
    if final and final.strip():
        print(final.strip())
    else:
        print("(no final answer returned)")

    if args.debug:
        sys.stderr.write(f"[debug] used path: {meta.get('path','?')}  source: {meta.get('reason','?')}\n")

if __name__ == "__main__":
    main()
