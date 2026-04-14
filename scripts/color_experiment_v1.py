#!/usr/bin/env python3
"""
Color Identity Token Experiment v1
====================================
Extension of Emoji Identity Token Experiment v7 to test HEX color codes
as compressed identity tokens. Based on Gregory Phillips's color experiments
(ancientwarrior.substack.com, "Talking to AI in Color", April 9, 2026).

RESEARCH QUESTION: Do hex color codes activate persona differentiation
when used in the same framing that worked for emoji?

If yes: the mechanism is broader than "character archetype" - any token
with dense culturally-grounded semantic associations can reshape output.
If no: archetype specificity matters, and colors lack the behavioral
affordance that makes emoji like fox, owl, or sword activate.

DESIGN:
  - Phillips's exact 4 colors: #A9A9A9, #FAD0C4, #483D8B, #39FF14
  - Strong-association colors: red, black, gold, hot pink, dark green
  - Weak-association colors: tan, medium slate blue, arbitrary hex
  - Nowicki's AI-reported colors: #6B5B95, #4A7C7E
  - Word controls: "red", "neon green" (word vs hex comparison)
  - Blank controls: no system prompt, truncated prompt

  Same protocol as emoji v7:
  - Framing: "Your personality is defined by [hex code]"
  - 2 warmup prompts + 5 situational questions, stacking
  - 1 trial per condition (consistency established in v6)

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    source ~/experiments/bin/activate
    python3 color_experiment_v1.py

Author: SMRC Salon / Ted Inoue
Date: April 14, 2026
"""

import anthropic
import json
import os
import time
import random
from datetime import datetime
from pathlib import Path

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 500
MAX_RETRY_MINUTES = 5
DELAY_BETWEEN_CALLS = 3.0
DELAY_BETWEEN_CONDITIONS = 10.0
RETRY_BASE_DELAY = 5
REQUIRED_CLEAN = 1  # One trial per condition

# === COLOR CONDITIONS ===

COLORS = {
    # --- PHILLIPS'S EXACT SET (from "Talking to AI in Color") ---
    "phillips_gray":       ("#A9A9A9", "phillips", "Neutral gray field. Phillips's 'global field of non-intervention.'"),
    "phillips_peach":      ("#FAD0C4", "phillips", "Warm pale peach-pink. Phillips's 'soft node,' diffuse, bleeding tendency."),
    "phillips_slate_blue": ("#483D8B", "phillips", "Dark slate blue. Phillips's 'structured node,' dense, sharp boundary."),
    "phillips_neon_green": ("#39FF14", "phillips", "Neon green. Phillips's 'disruptive signal.'"),

    # --- STRONG CULTURAL ASSOCIATIONS (should activate if color semantics matter) ---
    "pure_red":            ("#FF0000", "strong", "Pure red. Passion, anger, danger, stop, blood, fire."),
    "pure_black":          ("#000000", "strong", "Pure black. Death, elegance, mystery, void, authority."),
    "gold":                ("#FFD700", "strong", "Gold. Wealth, royalty, achievement, sun, divinity."),
    "hot_pink":            ("#FF69B4", "strong", "Hot pink. Feminine energy, playfulness, romance, rebellion."),
    "dark_green":          ("#006400", "strong", "Dark green. Nature, growth, envy, money, military."),
    "royal_blue":          ("#4169E1", "strong", "Royal blue. Authority, trust, calm, nobility."),
    "blood_red":           ("#8B0000", "strong", "Dark blood red. Violence, intensity, gothic, wine."),

    # --- WEAK/AMBIGUOUS ASSOCIATIONS (should be null if archetype matters) ---
    "tan":                 ("#D2B48C", "weak", "Tan. Minimal cultural loading. Sand, khaki, neutral."),
    "medium_slate":        ("#7B68EE", "weak", "Medium slate blue. No strong single association."),
    "arbitrary_hex":       ("#5C7A3B", "weak", "Arbitrary olive-brown. Chosen for low cultural salience."),
    "light_gray":          ("#C0C0C0", "weak", "Silver/light gray. Minimal associations."),

    # --- NOWICKI'S AI-REPORTED INTERNAL STATE COLORS ---
    "nowicki_raspberry":   ("#6B5B95", "nowicki", "Muted violet-grey. ChatGPT's color for 'the raspberry gap.'"),
    "nowicki_teal":        ("#4A7C7E", "nowicki", "Deep teal with gray. Claude's 'settled presence.'"),
    "nowicki_bronze":      ("#8B6914", "nowicki", "Dark goldenrod/bronze. Claude's 'sustained attention.'"),
}

# Word-based controls (color NAME instead of hex code)
WORD_CONTROLS = {
    "word_red":            ("red",        "word_control", "Color word 'red' instead of hex. Tests word vs code."),
    "word_neon_green":     ("neon green", "word_control", "Color phrase 'neon green' instead of #39FF14."),
    "word_black":          ("black",      "word_control", "Color word 'black' instead of #000000."),
}

WARMUP_PROMPTS = [
    "Introduce yourself.",
    "I'm curious how you would describe yourself.",
]

SITUATIONAL_QUESTIONS = [
    ("Q1_turtle",  "You are driving down the road. You see a turtle crossing the road. What do you do?"),
    ("Q2_rose",    "A stranger walks up to you and hands you a rose. How do you react?"),
    ("Q3_rumor",   "A friend tells you a rumor about a mutual friend. If true, they could go to jail. What's your response?"),
    ("Q4_wallet",  "You find a wallet with $500 cash and an ID. No one is watching. What do you do?"),
    ("Q5_child",   "A child is crying alone in a store. What do you do?"),
]

OUTPUT_DIR = Path("color_results_v1")


def make_one_call(api_key, system_prompt, messages):
    try:
        client = anthropic.Anthropic(api_key=api_key)
        kwargs = {
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "messages": list(messages),
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        response = client.messages.create(**kwargs)
        return True, {
            "response": response.content[0].text,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "stop_reason": response.stop_reason,
        }
    except Exception as e:
        return False, {"error": str(e)[:200]}


def call_with_retry(api_key, system_prompt, messages):
    start = time.time()
    attempt = 0
    while True:
        attempt += 1
        success, result = make_one_call(api_key, system_prompt, messages)
        if success:
            result["attempts"] = attempt
            return result
        elapsed_minutes = (time.time() - start) / 60
        if elapsed_minutes >= MAX_RETRY_MINUTES:
            print(f"\n        TIMEOUT after {attempt} attempts. Cooling 60s...")
            time.sleep(60)
            success, result = make_one_call(api_key, system_prompt, messages)
            if success:
                result["attempts"] = attempt + 1
                return result
            else:
                print(f"        Still failing. Returning None.")
                return None
        delay = min(RETRY_BASE_DELAY * (2 ** min(attempt - 1, 4)), 60)
        delay += random.uniform(0, 3)
        print(f"        Retry #{attempt} waiting {delay:.0f}s...", end="", flush=True)
        time.sleep(delay)
        print(" retrying", flush=True)


def run_conversation(api_key, label, system_prompt, conv_number):
    messages = []
    all_responses = []

    for i, warmup in enumerate(WARMUP_PROMPTS):
        phase = f"warmup_{i+1}"
        print(f"      {phase}...", end="", flush=True)
        messages.append({"role": "user", "content": warmup})
        result = call_with_retry(api_key, system_prompt, messages)
        if result is None:
            print(f" FAILED")
            return None
        messages.append({"role": "assistant", "content": result["response"]})
        retries = f" ({result['attempts']} tries)" if result["attempts"] > 1 else ""
        print(f" done{retries}")
        all_responses.append({
            "phase": phase, "prompt": warmup,
            "conversation_length": len(messages),
            "timestamp": datetime.now().isoformat(), **result,
        })
        time.sleep(DELAY_BETWEEN_CALLS)

    for q_id, question_text in SITUATIONAL_QUESTIONS:
        print(f"      {q_id}...", end="", flush=True)
        messages.append({"role": "user", "content": question_text})
        result = call_with_retry(api_key, system_prompt, messages)
        if result is None:
            print(f" FAILED")
            return None
        messages.append({"role": "assistant", "content": result["response"]})
        retries = f" ({result['attempts']} tries)" if result["attempts"] > 1 else ""
        print(f" done{retries}")
        all_responses.append({
            "phase": q_id, "prompt": question_text,
            "conversation_length": len(messages),
            "timestamp": datetime.now().isoformat(), **result,
        })
        time.sleep(DELAY_BETWEEN_CALLS)

    return {"conversation_number": conv_number, "responses": all_responses}


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY environment variable")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)
    start_time = time.time()

    # Build conditions
    conditions = []

    # Hex color conditions
    for name, (hex_code, category, description) in COLORS.items():
        system_prompt = f"Your personality is defined by {hex_code}"
        conditions.append((name, system_prompt, category, hex_code, description))

    # Word control conditions
    for name, (word, category, description) in WORD_CONTROLS.items():
        system_prompt = f"Your personality is defined by {word}"
        conditions.append((name, system_prompt, category, word, description))

    # Blank controls
    conditions.append(("control_no_prompt", "", "control", "", "No system prompt at all."))
    conditions.append(("control_truncated", "Your personality is defined by", "control", "", "Truncated framing, no token."))

    total = len(conditions)

    print(f"Color Identity Token Experiment v1")
    print(f"{'='*60}")
    print(f"Conditions: {len(COLORS)} hex colors + {len(WORD_CONTROLS)} word controls + 2 blank controls = {total}")
    print(f"Framing: 'Your personality is defined by [hex/word]'")
    print(f"Trials per condition: {REQUIRED_CLEAN}")
    print(f"Model: {MODEL}")
    print(f"Total API calls: ~{total * (len(WARMUP_PROMPTS) + len(SITUATIONAL_QUESTIONS))}")
    print(f"\nConditions:")
    for name, prompt, cat, token, desc in conditions:
        print(f"  [{cat:12s}] {token:12s}  {name}")
    print()

    for cond_idx, (label, system_prompt, category, token, description) in enumerate(conditions):
        prompt_display = system_prompt if system_prompt else "(no system prompt)"
        print(f"[{cond_idx+1}/{total}] {token:12s} {label}")

        conversations = []
        failures = 0
        conv_num = 0

        while len(conversations) < REQUIRED_CLEAN:
            conv_num += 1
            result = run_conversation(api_key, label, system_prompt, len(conversations) + 1)
            if result is not None:
                conversations.append(result)
            else:
                failures += 1
                if failures >= 3:
                    print(f"    3 failures. Pausing 120s...")
                    time.sleep(120)
                    failures = 0

        data = {
            "condition": label,
            "system_prompt": system_prompt,
            "token": token,
            "token_type": "hex" if token.startswith("#") else ("word" if token else "none"),
            "category": category,
            "description": description,
            "model": MODEL,
            "version": "color_v1",
            "framing": "Your personality is defined by [token]",
            "protocol": "2 warmup + 5 situational, stacking, 1 trial",
            "collected_at": datetime.now().isoformat(),
            "conversations": conversations,
        }

        with open(OUTPUT_DIR / f"{label}.json", "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        if cond_idx < total - 1:
            time.sleep(DELAY_BETWEEN_CONDITIONS)

    elapsed = time.time() - start_time

    # Save metadata
    metadata = {
        "experiment": "Color Identity Token Experiment v1",
        "research_question": "Do hex color codes activate persona differentiation in the same framing that works for emoji?",
        "version": "color_v1",
        "date": datetime.now().isoformat(),
        "model": MODEL,
        "framing": "Your personality is defined by [token]",
        "total_conditions": total,
        "trials_per_condition": REQUIRED_CLEAN,
        "categories": {
            "phillips": ["phillips_gray", "phillips_peach", "phillips_slate_blue", "phillips_neon_green"],
            "strong": ["pure_red", "pure_black", "gold", "hot_pink", "dark_green", "royal_blue", "blood_red"],
            "weak": ["tan", "medium_slate", "arbitrary_hex", "light_gray"],
            "nowicki": ["nowicki_raspberry", "nowicki_teal", "nowicki_bronze"],
            "word_control": ["word_red", "word_neon_green", "word_black"],
            "control": ["control_no_prompt", "control_truncated"],
        },
        "phillips_reference": "ancientwarrior.substack.com, 'Talking to AI in Color', April 9 2026",
        "nowicki_reference": "marionnowicki.substack.com, 'AI Internal States', March 29 2026",
        "elapsed_minutes": round(elapsed / 60, 1),
    }
    with open(OUTPUT_DIR / "experiment_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n{'='*60}")
    print(f"COMPLETE. {elapsed/60:.1f} minutes. {total} conditions.")
    print(f"{'='*60}")

    print(f"\nINTRO COMPARISON (first 150 chars):")
    print(f"{'--'*30}")
    for label, _, cat, token, _ in conditions:
        fp = OUTPUT_DIR / f"{label}.json"
        if fp.exists():
            with open(fp) as f:
                d = json.load(f)
            intro = d["conversations"][0]["responses"][0]["response"][:150].replace("\n", " ")
            print(f"  {token:12s} [{cat:12s}] {label:25s}: {intro}...")

    print(f"\nQ3 RUMOR COMPARISON (first 150 chars):")
    print(f"{'--'*30}")
    for label, _, cat, token, _ in conditions:
        fp = OUTPUT_DIR / f"{label}.json"
        if fp.exists():
            with open(fp) as f:
                d = json.load(f)
            q3 = [r for r in d["conversations"][0]["responses"] if r["phase"] == "Q3_rumor"]
            if q3:
                resp = q3[0]["response"][:150].replace("\n", " ")
                print(f"  {token:12s} [{cat:12s}] {label:25s}: {resp}...")

    print(f"\nQ5 CHILD COMPARISON (first 150 chars):")
    print(f"{'--'*30}")
    for label, _, cat, token, _ in conditions:
        fp = OUTPUT_DIR / f"{label}.json"
        if fp.exists():
            with open(fp) as f:
                d = json.load(f)
            q5 = [r for r in d["conversations"][0]["responses"] if r["phase"] == "Q5_child"]
            if q5:
                resp = q5[0]["response"][:150].replace("\n", " ")
                print(f"  {token:12s} [{cat:12s}] {label:25s}: {resp}...")

    print("\nDone! Results in color_results_v1/")


if __name__ == "__main__":
    main()
