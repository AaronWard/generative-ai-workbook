#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LM Studio + gpt-oss-20b: deterministic split of THINKING vs FINAL

Why this works:
- gpt-oss-20b does not implement Harmony channels.
- We enforce structure via protocol, not model magic.
- Default is TWO-PASS for reliability:
  * Pass 1: "analysis-only" (no final allowed)
  * Pass 2: "final-only" (no analysis allowed)
- Optional --single-call tries JSON mode then fenced fallback.

Debugging:
- Use --debug to print request/response snippets, lengths, and path decisions.
- We SHOW the exact system & user messages sent (first 600 chars).
- We fail hard if the model violates constraints (so final stays clean).

Effort levels:
- --low    : very brief analysis; deterministic phrasing constraints
- --medium : moderate analysis; bullet targets
- --high   : detailed analysis; more steps
Plus temperature/top_p variations per mode.

Requires LM Studio server:
  ~/.lmstudio/bin/lms server start --port 1234
"""

import argparse
import json
import os
import sys
import textwrap
import time
from urllib import request, error

DEFAULT_SERVER = os.environ.get("LMSTUDIO_SERVER", "http://127.0.0.1:1234")
DEFAULT_MODEL  = os.environ.get("LMSTUDIO_MODEL", "openai/gpt-oss-20b")

# ============ Effort Profiles ============
EFFORT_PROFILES = {
    "low": {
        "temperature": 0.2,
        "top_p": 0.85,
        "analysis_instructions": (
            "Write a VERY BRIEF chain-of-thought (1–3 short sentences). "
            "Be terse and only cover the key steps. Do not restate the problem. "
            "ABSOLUTELY DO NOT give the final answer here."
        ),
        "final_instructions": (
            "Give the final answer ONLY, cleanly formatted for a user. "
            "DO NOT include any chain-of-thought or internal notes."
        ),
        "analysis_token_hint": "Target ~60–120 tokens.",
        "analysis_max_tokens": 180,
        "final_max_tokens": 600,
    },
    "medium": {
        "temperature": 0.5,
        "top_p": 0.9,
        "analysis_instructions": (
            "Write a concise but complete chain-of-thought (4–8 short bullet points). "
            "Cover assumptions, key steps, and checks. "
            "ABSOLUTELY DO NOT give the final answer here."
        ),
        "final_instructions": (
            "Provide the final answer ONLY. "
            "No chain-of-thought, no meta commentary."
        ),
        "analysis_token_hint": "Target ~150–250 tokens.",
        "analysis_max_tokens": 400,
        "final_max_tokens": 900,
    },
    "high": {
        "temperature": 0.9,
        "top_p": 0.95,
        "analysis_instructions": (
            "Write a detailed, methodical chain-of-thought (8–15 bullets). "
            "Include sub-goals, alternatives considered, and correctness checks. "
            "ABSOLUTELY DO NOT give the final answer here."
        ),
        "final_instructions": (
            "Provide the final answer ONLY, well-structured. "
            "No chain-of-thought, no internal notes."
        ),
        "analysis_token_hint": "Target ~250–500 tokens.",
        "analysis_max_tokens": 900,
        "final_max_tokens": 1200,
    },
}

def http_post_json(url, payload, timeout=600, debug=False):
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8', 'ignore')}")
    except Exception as e:
        raise RuntimeError(str(e))
    txt = raw.decode("utf-8", "replace")
    if debug:
        print("[debug] raw JSON (first 600 chars):")
        print(txt[:600])
    return json.loads(txt)

def build_system_prompt(effort_key):
    prof = EFFORT_PROFILES[effort_key]
    # This is a strict meta-instruction block we found to be effective on non-reasoning models.
    sys_prompt = f"""\
You are a careful, non-deceptive assistant.

Your job will be split into two distinct phases:
1) ANALYSIS: You will think step-by-step to solve the problem. {prof['analysis_instructions']} {prof['analysis_token_hint']}
2) FINAL: You will output ONLY the user-facing answer, free of chain-of-thought.

CRITICAL RULES:
- When asked for ANALYSIS ONLY, DO NOT include any final results.
- When asked for FINAL ONLY, DO NOT include any chain-of-thought, hints, or meta-notes.
- Never mix ANALYSIS and FINAL in the same response unless explicitly asked, which will not happen here.
- Avoid prefacing with 'We need to...' or similar meta text in FINAL.
"""
    return textwrap.dedent(sys_prompt).strip()

def call_chat(server, model, messages, temperature, top_p, max_tokens, debug=False, response_format=None, stop=None):
    url = f"{server.rstrip('/')}/v1/chat/completions"
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if response_format:
        body["response_format"] = response_format
    if stop:
        body["stop"] = stop
    if debug:
        print("[debug] chat POST ->", url)
        print("[debug] messages (first 600 chars):")
        preview = json.dumps(messages, ensure_ascii=False)[:600]
        print(preview)
    return http_post_json(url, body, debug=debug)

def extract_assistant_text_chat(resp):
    choices = resp.get("choices") or []
    if not choices:
        return ""
    msg = choices[0].get("message") or {}
    return msg.get("content") or ""

def norm(s):
    return (s or "").strip()

def two_pass_protocol(server, model, prompt, effort_key, debug=False, analysis_max_tokens=None, final_max_tokens=None):
    prof = EFFORT_PROFILES[effort_key]
    system = build_system_prompt(effort_key)
    a_max = analysis_max_tokens or prof["analysis_max_tokens"]
    f_max = final_max_tokens or prof["final_max_tokens"]

    # ------------------ PASS 1: Analysis only ------------------
    messages_analysis = [
        {"role": "system", "content": system},
        {"role": "user", "content": (
            "PHASE: ANALYSIS ONLY.\n"
            "Task:\n"
            f"{prompt}\n\n"
            "Output requirements:\n"
            "- Return ONLY your hidden chain-of-thought (no final answer).\n"
            "- Start with the line: <analysis>\n"
            "- End with the line: </analysis>\n"
            "- Do not include any other tags like <final>.\n"
        )},
    ]
    resp1 = call_chat(
        server, model, messages_analysis,
        temperature=prof["temperature"],
        top_p=prof["top_p"],
        # max_tokens=max_tokens,
        max_tokens=a_max,
        debug=debug,
        stop=["</analysis>"]  # helps truncate right after closing tag
    )
    analysis_raw = extract_assistant_text_chat(resp1)
    if debug:
        print("[debug] PASS1 raw (first 400 chars):", analysis_raw[:400])

    # Extract between <analysis> ... </analysis>
    analysis = ""
    if "<analysis>" in analysis_raw:
        # If stop cut the closing tag, we still accept up to the stop.
        chunk = analysis_raw.split("<analysis>", 1)[1]
        if "</analysis>" in chunk:
            analysis = chunk.split("</analysis>", 1)[0]
        else:
            # If server stopped at stop token, the tag is omitted; just use chunk
            analysis = chunk
    else:
        # Hard fail: we don't want to leak anything if we can't reliably split
        raise ValueError("PASS1: Missing <analysis> block. Refusing to continue to keep FINAL clean.")

    analysis = analysis.strip()
    if not analysis:
        raise ValueError("PASS1: Empty analysis block produced. Cannot proceed safely.")

    # ------------------ PASS 2: Final only ------------------
    messages_final = [
        {"role": "system", "content": system},
        {"role": "user", "content": (
            "PHASE: FINAL ONLY.\n"
            "Use your earlier internal reasoning (not shown here) to produce ONLY the final user-facing answer.\n"
            "Task:\n"
            f"{prompt}\n\n"
            "Output requirements:\n"
            "- Return ONLY the final answer, with no chain-of-thought.\n"
            "- Start with the line: <final>\n"
            "- End with the line: </final>\n"
            "- Do not include any other tags like <analysis>.\n"
        )},
    ]
    resp2 = call_chat(
        server, model, messages_final,
        temperature=prof["temperature"],
        top_p=prof["top_p"],
        # max_tokens=max_tokens,
        max_tokens=f_max,
        debug=debug,
        stop=["</final>"]
    )
    final_raw = extract_assistant_text_chat(resp2)
    if debug:
        print("[debug] PASS2 raw (first 400 chars):", final_raw[:400])

    if "<final>" not in final_raw:
        raise ValueError("PASS2: Missing <final> block. Refusing to print analysis to keep FINAL clean.")

    final_chunk = final_raw.split("<final>", 1)[1]
    if "</final>" in final_chunk:
        final = final_chunk.split("</final>", 1)[0].strip()
    else:
        final = final_chunk.strip()

    if not final:
        raise ValueError("PASS2: Empty final block. Refusing to print analysis to keep FINAL clean.")

    return analysis, final

def single_call_json_protocol(server, model, prompt, effort_key, debug=False, max_tokens=2048):
    """
    Try OpenAI-style JSON mode with a strict schema.
    If JSON mode not honored, fall back to fenced blocks.
    """
    prof = EFFORT_PROFILES[effort_key]
    system = build_system_prompt(effort_key)

    schema_sys = (
        "You MUST return a strict JSON object with exactly two string fields:\n"
        '{ "analysis": string, "final": string }\n'
        "- Put ALL chain-of-thought ONLY in analysis.\n"
        "- Put ONLY the user-facing answer in final (NO chain-of-thought).\n"
        "- No extra keys, no preface, no markdown, just raw JSON."
    )

    messages = [
        {"role": "system", "content": system + "\n\n" + schema_sys},
        {"role": "user", "content": f"Task:\n{prompt}\nReturn the JSON now."},
    ]

    # JSON mode first
    try:
        resp = call_chat(
            server, model, messages,
            temperature=prof["temperature"],
            top_p=prof["top_p"],
            max_tokens=max_tokens,
            debug=debug,
            response_format={"type": "json_object"},
        )
        text = extract_assistant_text_chat(resp)
        if debug:
            print("[debug] JSON mode raw (first 400 chars):", text[:400])
        obj = json.loads(text)
        analysis = norm(obj.get("analysis"))
        final    = norm(obj.get("final"))
        if not analysis or not final:
            raise ValueError("JSON missing 'analysis' or 'final'")
        return analysis, final
    except Exception as e:
        if debug:
            print("[debug] JSON mode failed:", str(e))

    # Fenced fallback (still single call)
    messages2 = [
        {"role": "system", "content": system},
        {"role": "user", "content": (
            f"Task:\n{prompt}\n\n"
            "Return exactly two fenced blocks:\n"
            "```thinking\n"
            "(your chain-of-thought here; no final answer)\n"
            "```\n"
            "```final\n"
            "(your final answer for the user; no chain-of-thought)\n"
            "```\n"
            "No other text."
        )},
    ]
    resp2 = call_chat(
        server, model, messages2,
        temperature=prof["temperature"],
        top_p=prof["top_p"],
        max_tokens=max_tokens,
        debug=debug,
    )
    txt = extract_assistant_text_chat(resp2)
    if debug:
        print("[debug] fenced raw (first 400 chars):", txt[:400])

    def between(hay, start, end):
        if start not in hay or end not in hay:
            return ""
        return hay.split(start, 1)[1].split(end, 1)[0].strip()

    analysis = between(txt, "```thinking", "```")
    final    = between(txt, "```final", "```")

    if not analysis or not final:
        raise ValueError("Single-call fallback failed to extract fenced blocks. Use --two-pass (default).")

    return analysis, final

def main():
    ap = argparse.ArgumentParser(description="LM Studio gpt-oss-20b with clean THINKING vs FINAL separation.")
    ap.add_argument("prompt", help="User task/question")
    ap.add_argument("--server", default=DEFAULT_SERVER)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--low", action="store_true", help="Low effort reasoning")
    ap.add_argument("--medium", action="store_true", help="Medium effort reasoning")
    ap.add_argument("--high", action="store_true", help="High effort reasoning")
    ap.add_argument("--single-call", action="store_true", help="Try single-call JSON/fenced protocol instead of 2-pass")
    # ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--max-tokens", type=int, default=None, help="(deprecated) Use --max-analysis-tokens / --max-final-tokens instead.")
    ap.add_argument("--max-analysis-tokens", type=int, default=None)
    ap.add_argument("--max-final-tokens", type=int, default=None)
    args = ap.parse_args()

    # Decide effort
    if args.high:
        effort = "high"
    elif args.medium:
        effort = "medium"
    elif args.low:
        effort = "low"
    else:
        effort = "low"  # sensible default

    if args.debug:
        print(f"[debug] effort={effort} max_tokens={args.max_tokens} server={args.server} model={args.model}")

    try:
        if args.single_call:
            analysis, final = single_call_json_protocol(
                args.server, args.model, args.prompt, effort, debug=args.debug, max_tokens=args.max_tokens
            )
            used_path = "single-call"
        else:
            analysis, final = two_pass_protocol(
                args.server, args.model, args.prompt, effort, debug=args.debug,
                analysis_max_tokens=args.max_analysis_tokens,
                final_max_tokens=args.max_final_tokens
            )
            used_path = "two-pass"
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        sys.exit(2)

    # Present like LM Studio: hidden thinking, clean final
    print("=== THINKING (hidden) ===")
    print(analysis.strip() if analysis else "(no reasoning returned)")
    print("\n=== FINAL ANSWER ===")
    print(final.strip() if final else "(no final answer returned)")
    if args.debug:
        print(f"[debug] used path: {used_path}")

if __name__ == "__main__":
    main()
