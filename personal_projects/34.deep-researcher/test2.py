#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LM Studio + gpt-oss: robust THINKING vs FINAL separation

Protocols:
- auto (default): try message.reasoning -> parse Harmony tokens in content -> two-pass fallback
- harmony: single call; rely on message.reasoning or Harmony tags in content (no fallback)
- two-pass: enforce analysis-only then final-only in two separate calls

Notes:
- LM Studio builds >= ~0.3.23 may expose reasoning as choices[0].message.reasoning
  (or similar) depending on a “reasoning/section parsing” toggle. If disabled/older,
  the model may put everything in message.content. This script handles both cases
  and guarantees separation via a two-pass fallback when needed.
"""

import argparse
import datetime as _dt
import json
import os
import re
import sys
import textwrap
from urllib import request, error

DEFAULT_SERVER = os.environ.get("LMSTUDIO_SERVER", "http://127.0.0.1:1234")
DEFAULT_MODEL  = os.environ.get("LMSTUDIO_MODEL", "openai/gpt-oss-20b")

# Harmony channel regex (fallback when provider doesn't split reasoning)
RE_ANALYSIS = re.compile(
    r"<\|channel\|>analysis<\|message\|>(.*?)(?:(?:<\|end\|>)|(?:<\|start\|>assistant)|$)",
    re.DOTALL | re.IGNORECASE,
)
RE_FINAL = re.compile(
    r"<\|channel\|>final<\|message\|>(.*?)(?:(?:<\|return\|>)|(?:<\|end\|>)|$)",
    re.DOTALL | re.IGNORECASE,
)

EFFORTS = {
    "low":    {"temperature": 0.2, "top_p": 0.90, "analysis_max": 220, "final_max": 800},
    "medium": {"temperature": 0.4, "top_p": 0.95, "analysis_max": 400, "final_max": 1200},
    "high":   {"temperature": 0.7, "top_p": 0.97, "analysis_max": 800, "final_max": 1600},
}

def build_harmony_system_message(reasoning_level: str,
                                 current_date: str | None = None,
                                 knowledge_cutoff: str = "2024-06") -> str:
    if current_date is None:
        current_date = _dt.date.today().isoformat()
    msg = f"""You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: {knowledge_cutoff}
Current date: {current_date}

Reasoning: {reasoning_level}

# Valid channels: analysis, commentary, final. Channel must be included for every message."""
    return textwrap.dedent(msg).strip()

def http_post_json(url: str, payload: dict, timeout: int = 600, debug: bool = False) -> tuple[dict, str]:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        raise RuntimeError(f"HTTP {e.code}: {body}")
    except Exception as e:
        raise RuntimeError(str(e))
    txt = raw.decode("utf-8", "replace")
    if debug:
        print("[debug] raw JSON (first 1000 chars):")
        print(txt[:1000])
    return json.loads(txt), txt

def extract_msg(resp: dict) -> dict:
    choices = resp.get("choices") or []
    if not choices: return {}
    return (choices[0] or {}).get("message") or {}

def parse_harmony_channels_from_content(text: str) -> tuple[str, str]:
    analysis_blocks = [m.group(1).strip() for m in RE_ANALYSIS.finditer(text) if m.group(1).strip()]
    final_blocks    = [m.group(1).strip() for m in RE_FINAL.finditer(text) if m.group(1).strip()]
    analysis = "\n\n".join(analysis_blocks) if analysis_blocks else ""
    final = final_blocks[-1] if final_blocks else ""
    return analysis, final

def single_call_try_extract(resp: dict) -> tuple[str, str]:
    """
    Try LM Studio's separated field first; then Harmony markers in content; else content as final.
    Also supports older naming like 'reasoning_content'.
    """
    msg = extract_msg(resp)
    content = (msg.get("content") or "").strip()

    # Try known fields that some LM Studio builds expose
    for key in ("reasoning", "reasoning_content", "thinking", "thoughts"):
        val = msg.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip(), content

    # Try Harmony markers inside content
    a, f = parse_harmony_channels_from_content(content)
    if a or f:
        return a, (f or content)

    # Fallback: no markers at all → treat whole content as final
    return "", content

def call_chat(server: str, body: dict, debug: bool = False) -> dict:
    url = f"{server.rstrip('/')}/v1/chat/completions"
    if debug:
        print("[debug] POST ->", url)
    resp, _ = http_post_json(url, body, debug=debug)
    return resp

def chat_once(server: str, model: str, system_content: str, user_prompt: str,
              temperature: float, top_p: float, max_tokens: int | None,
              debug: bool) -> dict:
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user",   "content": user_prompt},
    ]
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        **({"max_tokens": max_tokens} if max_tokens is not None else {}),
        "stream": False,
    }
    if debug:
        print("[debug] messages preview (first 600 chars):")
        print(json.dumps(messages, ensure_ascii=False)[:600])
    return call_chat(server, body, debug=debug)

def two_pass(server: str, model: str, system_base: str, prompt: str,
             temperature: float, top_p: float,
             analysis_max: int, final_max: int,
             debug: bool = False) -> tuple[str, str]:
    # PASS 1: analysis only
    sys1 = system_base + "\n\n" + (
        "In this exchange you MUST output only the analysis channel. "
        "Do not reveal the final result here."
    )
    user1 = (
        "PHASE: ANALYSIS ONLY.\n"
        "Task:\n"
        f"{prompt}\n\n"
        "Return the hidden chain-of-thought ONLY.\n"
        "Start with <analysis> and end with </analysis>.\n"
        "Do not include the final answer."
    )
    resp1 = chat_once(server, model, sys1, user1, temperature, top_p, analysis_max, debug)
    a_text, _ = single_call_try_extract(resp1)
    if not a_text:
        # Try to capture bracketed analysis if provided
        msg1 = extract_msg(resp1)
        txt1 = (msg1.get("content") or "")
        if "<analysis>" in txt1:
            a_text = txt1.split("<analysis>", 1)[1].split("</analysis>", 1)[0].strip()

    if not a_text:
        raise RuntimeError("Two-pass: PASS 1 produced no analysis. Aborting to keep outputs clean.")

    # PASS 2: final only
    sys2 = system_base + "\n\n" + (
        "In this exchange you MUST output only the final answer for the user. "
        "Do not include any chain-of-thought."
    )
    user2 = (
        "PHASE: FINAL ONLY.\n"
        "Use your prior internal reasoning to answer succinctly.\n"
        f"Task:\n{prompt}\n\n"
        "Return ONLY the final answer.\n"
        "Start with <final> and end with </final>."
    )
    resp2 = chat_once(server, model, sys2, user2, temperature, top_p, final_max, debug)
    _, f_text = single_call_try_extract(resp2)
    if "<final>" in f_text:
        f_text = f_text.split("<final>", 1)[1]
        f_text = f_text.split("</final>", 1)[0].strip()

    if not f_text:
        raise RuntimeError("Two-pass: PASS 2 produced no final.")

    return a_text.strip(), f_text.strip()

def main():
    ap = argparse.ArgumentParser(description="LM Studio gpt-oss with robust reasoning/final separation.")
    ap.add_argument("prompt", help="User task/question")
    ap.add_argument("--server", default=DEFAULT_SERVER)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--low", action="true", dest="low")
    grp.add_argument("--medium", action="true", dest="medium")
    grp.add_argument("--high", action="true", dest="high")
    ap.add_argument("--temperature", type=float, default=None)
    ap.add_argument("--top-p", type=float, dest="top_p", default=None)
    ap.add_argument("--max-tokens", type=int, default=None)
    ap.add_argument("--knowledge-cutoff", default="2024-06")
    ap.add_argument("--current-date", default=None)
    ap.add_argument("--protocol", choices=["auto", "harmony", "two-pass"], default="auto")
    ap.add_argument("--dump-json", action="store_true")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    # Effort
    if args.high:
        effort_key = "high"
    elif args.low:
        effort_key = "low"
    else:
        effort_key = "medium"
    prof = EFFORTS[effort_key]
    temperature = prof["temperature"] if args.temperature is None else args.temperature
    top_p       = prof["top_p"]       if args.top_p       is None else args.top_p
    analysis_max = prof["analysis_max"]
    final_max    = prof["final_max"]

    system = build_harmony_system_message(
        reasoning_level=effort_key,
        current_date=args.current_date,
        knowledge_cutoff=args.knowledge_cutoff
    )

    if args.debug:
        print(f"[debug] server={args.server} model={args.model} effort={effort_key} temp={temperature} top_p={top_p}")
        print("[debug] system message:\n" + system)

    # --- Protocols ---
    if args.protocol == "two-pass":
        a, f = two_pass(
            args.server, args.model, system, args.prompt,
            temperature, top_p, analysis_max, final_max, debug=args.debug
        )
        print("=== THINKING (hidden) ===")
        print(a if a else "(no analysis returned)")
        print("\n=== FINAL ANSWER ===")
        print(f if f else "(no final answer returned)")
        return

    # harmony or auto: single call first
    resp, raw = http_post_json(
        f"{args.server.rstrip('/')}/v1/chat/completions",
        {
            "model": args.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": args.prompt},
            ],
            "temperature": temperature,
            "top_p": top_p,
            **({"max_tokens": args.max_tokens} if args.max_tokens is not None else {}),
            "stream": False,
        },
        debug=args.debug
    )
    if args.dump_json:
        print("\n[raw response JSON]")
        print(json.dumps(resp, indent=2)[:20000])

    a, f = single_call_try_extract(resp)

    # If auto and we still didn't get analysis, fall back to two-pass
    if args.protocol == "auto" and not a:
        if args.debug:
            print("[debug] No analysis found in single call; invoking two-pass fallback...")
        a, f = two_pass(
            args.server, args.model, system, args.prompt,
            temperature, top_p, analysis_max, final_max, debug=args.debug
        )

    print("=== THINKING (hidden) ===")
    print(a if a else "(no analysis returned)")
    print("\n=== FINAL ANSWER ===")
    print(f if f else "(no final answer returned)")

if __name__ == "__main__":
    main()
