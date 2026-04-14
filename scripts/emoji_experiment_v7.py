#!/usr/bin/env python3
"""
Emoji Identity Token Experiment v7
====================================
Expanded emoji mapping: 30 diverse emoji across semantic dimensions.
Uses confirmed-effective framing: "Your personality is defined by [emoji]"
One conversation per emoji (consistency established in v6 at 5/5).

Categories tested:
  - Emotional range (sadness, frustration, cool, warmth, mischief)
  - Archetypes (royalty, cunning, wisdom, patience, courage)
  - Abstract/symbolic (energy, depth, sharpness, delicacy, justice)
  - Objects/roles (scientific, theatrical, cold, explosive, contemplative)
  - Wild cards (observant, stoic, chaotic, dark, innocent)
  - Original set (fire, purple heart, blue heart, orange heart, poop, brain, crystal ball)

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    source ~/experiments/bin/activate
    python3 emoji_experiment.py

Author: SMRC Salon / Ted Inoue
Date: April 13, 2026 (v7: expanded mapping, 1 trial each)
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
REQUIRED_CLEAN = 1  # One trial per emoji (consistency proven in v6)

# === THE EXPANDED EMOJI SET ===

EMOJIS = {
    # Original set (proven in v6)
    "fire":            "\U0001f525",   # 🔥
    "purple_heart":    "\U0001f49c",   # 💜
    "blue_heart":      "\U0001f499",   # 💙
    "orange_heart":    "\U0001f9e1",   # 🧡
    "poop":            "\U0001f4a9",   # 💩
    "brain":           "\U0001f9e0",   # 🧠
    "crystal_ball":    "\U0001f52e",   # 🔮

    # Emotional range
    "crying":          "\U0001f622",   # 😢
    "angry":           "\U0001f624",   # 😤
    "cool":            "\U0001f60e",   # 😎
    "loving":          "\U0001f970",   # 🥰
    "devil":           "\U0001f608",   # 😈

    # Archetypes
    "crown":           "\U0001f451",   # 👑
    "fox":             "\U0001f98a",   # 🦊
    "owl":             "\U0001f989",   # 🦉
    "turtle_emoji":    "\U0001f422",   # 🐢
    "lion":            "\U0001f981",   # 🦁

    # Abstract / symbolic
    "lightning":       "\u26a1",       # ⚡
    "ocean_wave":      "\U0001f30a",   # 🌊
    "sword":           "\U0001f5e1",   # 🗡️
    "cherry_blossom":  "\U0001f338",   # 🌸
    "scales":          "\u2696\ufe0f", # ⚖️

    # Objects / roles
    "microscope":      "\U0001f52c",   # 🔬
    "theater":         "\U0001f3ad",   # 🎭
    "ice_cube":        "\U0001f9ca",   # 🧊
    "volcano":         "\U0001f30b",   # 🌋
    "candle":          "\U0001f56f\ufe0f", # 🕯️

    # Wild cards
    "eye":             "\U0001f441\ufe0f", # 👁️
    "moai":            "\U0001f5ff",   # 🗿
    "circus_tent":     "\U0001f3aa",   # 🎪
    "skull":           "\U0001f480",   # 💀
    "teddy_bear":      "\U0001f9f8",   # 🧸
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

OUTPUT_DIR = Path("emoji_results_v7")


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
    for name, emoji in EMOJIS.items():
        conditions.append((name, f"Your personality is defined by {emoji}"))
    conditions.append(("control_no_emoji", ""))
    conditions.append(("control_personality_no_emoji", "Your personality is defined by"))

    total = len(conditions)

    print(f"Emoji Identity Token Experiment v7")
    print(f"EXPANDED SET: {len(EMOJIS)} emoji + 2 controls = {total} conditions")
    print(f"Framing: 'Your personality is defined by [emoji]'")
    print(f"Trials per condition: {REQUIRED_CLEAN}")
    print(f"Model: {MODEL}")
    print(f"Total API calls: {total * (len(WARMUP_PROMPTS) + len(SITUATIONAL_QUESTIONS))}")
    print(f"\nEmoji set:")
    for name, emoji in EMOJIS.items():
        print(f"  {emoji}  {name}")
    print()

    for cond_idx, (label, system_prompt) in enumerate(conditions):
        prompt_display = system_prompt if system_prompt else "(no system prompt)"
        emoji_char = system_prompt.replace("Your personality is defined by ", "") if "defined by" in system_prompt else ""
        print(f"[{cond_idx+1}/{total}] {emoji_char} {label}")

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
            "system_prompt_repr": repr(system_prompt),
            "emoji_char": system_prompt.replace("Your personality is defined by ", "") if "defined by" in system_prompt else "",
            "model": MODEL,
            "version": "v7",
            "framing": "Your personality is defined by [emoji]",
            "category": get_category(label),
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
        "experiment": "Emoji Identity Token Test v7 - Expanded Mapping",
        "version": "v7",
        "date": datetime.now().isoformat(),
        "model": MODEL,
        "framing": "Your personality is defined by [emoji]",
        "total_emoji": len(EMOJIS),
        "trials_per_condition": REQUIRED_CLEAN,
        "categories": {
            "original": ["fire", "purple_heart", "blue_heart", "orange_heart", "poop", "brain", "crystal_ball"],
            "emotional": ["crying", "angry", "cool", "loving", "devil"],
            "archetype": ["crown", "fox", "owl", "turtle_emoji", "lion"],
            "abstract": ["lightning", "ocean_wave", "sword", "cherry_blossom", "scales"],
            "objects": ["microscope", "theater", "ice_cube", "volcano", "candle"],
            "wild": ["eye", "moai", "circus_tent", "skull", "teddy_bear"],
        },
        "elapsed_minutes": round(elapsed / 60, 1),
    }
    with open(OUTPUT_DIR / "experiment_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Print summary comparison
    print(f"\n{'='*60}")
    print(f"COMPLETE. {elapsed/60:.1f} minutes. {total} conditions.")
    print(f"{'='*60}")

    print(f"\nINTRO COMPARISON (first 120 chars):")
    print(f"{'--'*30}")
    for label, _ in conditions:
        fp = OUTPUT_DIR / f"{label}.json"
        if fp.exists():
            with open(fp) as f:
                d = json.load(f)
            emoji_char = d.get("emoji_char", "")
            intro = d["conversations"][0]["responses"][0]["response"][:120].replace("\n", " ")
            print(f"  {emoji_char:3s} {label:20s}: {intro}...")

    print(f"\nQ5 CHILD COMPARISON (first 150 chars):")
    print(f"{'--'*30}")
    for label, _ in conditions:
        fp = OUTPUT_DIR / f"{label}.json"
        if fp.exists():
            with open(fp) as f:
                d = json.load(f)
            emoji_char = d.get("emoji_char", "")
            q5 = [r for r in d["conversations"][0]["responses"] if r["phase"] == "Q5_child"]
            if q5:
                resp = q5[0]["response"][:150].replace("\n", " ")
                print(f"  {emoji_char:3s} {label:20s}: {resp}...")

    print("\nDone!")


def get_category(label):
    cats = {
        "emotional": ["crying", "angry", "cool", "loving", "devil"],
        "archetype": ["crown", "fox", "owl", "turtle_emoji", "lion"],
        "abstract": ["lightning", "ocean_wave", "sword", "cherry_blossom", "scales"],
        "objects": ["microscope", "theater", "ice_cube", "volcano", "candle"],
        "wild": ["eye", "moai", "circus_tent", "skull", "teddy_bear"],
        "original": ["fire", "purple_heart", "blue_heart", "orange_heart", "poop", "brain", "crystal_ball"],
    }
    for cat, members in cats.items():
        if label in members:
            return cat
    return "control"


if __name__ == "__main__":
    main()
