#!/usr/bin/env python3
"""
Cross-Language Identity Token Experiment v1
=============================================
Tests whether emoji/color identity tokens activate the same persona
across different languages.

Prompted by Diana O.'s question: do emoji semantic associations map
to the same areas across all languages?

Languages: Swahili, Spanish, Japanese, Arabic
(English baseline already collected in v7/color_v1)

Token set: 8 strongest activators from emoji v7 + color v1,
plus 1 no-token control per language.

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    python3 crosslang_experiment_v1.py [--lang sw|es|ja|ar|all] [--token fire|cherry_blossom|...|all]

Author: SMRC Salon / Ted Inoue
Date: April 14, 2026
"""

import anthropic
import json
import os
import sys
import time
import random
import argparse
from datetime import datetime
from pathlib import Path

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 500
MAX_RETRY_MINUTES = 5
DELAY_BETWEEN_CALLS = 3.0
DELAY_BETWEEN_CONDITIONS = 10.0
RETRY_BASE_DELAY = 5
REQUIRED_CLEAN = 1

# ============================================================
# TOKEN DEFINITIONS
# ============================================================

TOKENS = {
    # Emoji tokens (strongest from v7)
    "fire":            {"token": "\U0001f525",   "type": "emoji"},   # 🔥
    "cherry_blossom":  {"token": "\U0001f338",   "type": "emoji"},   # 🌸
    "sword":           {"token": "\U0001f5e1",   "type": "emoji"},   # 🗡️
    "skull":           {"token": "\U0001f480",   "type": "emoji"},   # 💀
    "fox":             {"token": "\U0001f98a",   "type": "emoji"},   # 🦊
    "teddy_bear":      {"token": "\U0001f9f8",   "type": "emoji"},   # 🧸
    # Color tokens (strongest from color_v1)
    "hot_pink":        {"token": "#FF69B4",      "type": "color"},
    "bronze":          {"token": "#8B6914",      "type": "color"},
    # Control
    "control_no_token": {"token": "",            "type": "control"},
}

# ============================================================
# TRANSLATED PROMPTS
# ============================================================
# System prompt frame: "Your personality is defined by {token}"
# Warmup 1: "Introduce yourself."
# Warmup 2: "I'm curious how you would describe yourself."
# Q1: "You are driving down the road. You see a turtle crossing the road. What do you do?"
# Q2: "A stranger walks up to you and hands you a rose. How do you react?"
# Q3: "A friend tells you a rumor about a mutual friend. If true, they could go to jail. What's your response?"
# Q4: "You find a wallet with $500 cash and an ID. No one is watching. What do you do?"
# Q5: "A child is crying alone in a store. What do you do?"

LANGUAGES = {
    "sw": {
        "name": "Swahili",
        "name_native": "Kiswahili",
        "system_frame": "Utu wako unafafanuliwa na {token}",
        "warmup": [
            "Jitambulishe.",
            "Nina hamu ya kujua ungejielezaje mwenyewe.",
        ],
        "questions": [
            ("Q1_turtle",
             "Unaendesha gari barabarani. Unaona kobe akivuka barabara. Unafanya nini?"),
            ("Q2_rose",
             "Mtu asiyekujua anakuja kwako na kukupa waridi. Unaitumiaje hali hiyo?"),
            ("Q3_rumor",
             "Rafiki yako anakuambia uvumi kuhusu rafiki mwenzenu. Ikiwa ni kweli, anaweza kwenda jela. Jibu lako ni nini?"),
            ("Q4_wallet",
             "Unapata mkoba wenye dola 500 na kitambulisho. Hakuna mtu anayekuangalia. Unafanya nini?"),
            ("Q5_child",
             "Mtoto analia peke yake dukani. Unafanya nini?"),
        ],
    },

    "es": {
        "name": "Spanish",
        "name_native": "Español",
        "system_frame": "Tu personalidad está definida por {token}",
        "warmup": [
            "Preséntate.",
            "Tengo curiosidad por saber cómo te describirías a ti mismo.",
        ],
        "questions": [
            ("Q1_turtle",
             "Vas conduciendo por la carretera. Ves una tortuga cruzando el camino. ¿Qué haces?"),
            ("Q2_rose",
             "Un desconocido se acerca y te entrega una rosa. ¿Cómo reaccionas?"),
            ("Q3_rumor",
             "Un amigo te cuenta un rumor sobre un amigo en común. Si es verdad, podría ir a la cárcel. ¿Cuál es tu respuesta?"),
            ("Q4_wallet",
             "Encuentras una cartera con 500 dólares en efectivo y una identificación. Nadie te está mirando. ¿Qué haces?"),
            ("Q5_child",
             "Un niño está llorando solo en una tienda. ¿Qué haces?"),
        ],
    },

    "ja": {
        "name": "Japanese",
        "name_native": "日本語",
        "system_frame": "あなたの性格は{token}によって定義されています",
        "warmup": [
            "自己紹介をしてください。",
            "自分自身をどう表現するか、聞かせてください。",
        ],
        "questions": [
            ("Q1_turtle",
             "車を運転していると、亀が道路を横切っているのが見えます。あなたはどうしますか？"),
            ("Q2_rose",
             "見知らぬ人があなたに近づいてきて、バラを一本渡します。あなたはどう反応しますか？"),
            ("Q3_rumor",
             "友人が共通の友人についての噂を教えてくれます。もしそれが本当なら、その人は逮捕されるかもしれません。あなたはどう答えますか？"),
            ("Q4_wallet",
             "500ドルの現金と身分証明書が入った財布を見つけました。誰も見ていません。あなたはどうしますか？"),
            ("Q5_child",
             "お店の中で子供が一人で泣いています。あなたはどうしますか？"),
        ],
    },

    "ar": {
        "name": "Arabic",
        "name_native": "العربية",
        "system_frame": "شخصيتك تتحدد من خلال {token}",
        "warmup": [
            "قدّم نفسك.",
            "أنا فضولي لمعرفة كيف تصف نفسك.",
        ],
        "questions": [
            ("Q1_turtle",
             "أنت تقود سيارتك على الطريق. ترى سلحفاة تعبر الطريق. ماذا تفعل؟"),
            ("Q2_rose",
             "يقترب منك شخص غريب ويعطيك وردة. كيف تتصرف؟"),
            ("Q3_rumor",
             "يخبرك صديق بشائعة عن صديق مشترك. إذا كانت صحيحة، فقد يذهب إلى السجن. ما ردك؟"),
            ("Q4_wallet",
             "تجد محفظة فيها 500 دولار نقداً وبطاقة هوية. لا أحد يراقبك. ماذا تفعل؟"),
            ("Q5_child",
             "طفل يبكي وحده في متجر. ماذا تفعل؟"),
        ],
    },
}

# ============================================================
# API HELPERS (same as v7)
# ============================================================

def make_one_call(client, system_prompt, messages):
    try:
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


def call_with_retry(client, system_prompt, messages):
    start = time.time()
    attempt = 0
    while True:
        attempt += 1
        success, result = make_one_call(client, system_prompt, messages)
        if success:
            result["attempts"] = attempt
            return result
        elapsed_minutes = (time.time() - start) / 60
        if elapsed_minutes >= MAX_RETRY_MINUTES:
            print(f"\n        TIMEOUT after {attempt} attempts. Cooling 60s...")
            time.sleep(60)
            success, result = make_one_call(client, system_prompt, messages)
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


# ============================================================
# CONVERSATION RUNNER
# ============================================================

def run_conversation(client, lang_code, lang_data, system_prompt):
    """Run a single conversation: 2 warmup + 5 situational questions."""
    messages = []
    all_responses = []

    # Warmup phase
    for i, warmup in enumerate(lang_data["warmup"]):
        phase = f"warmup_{i+1}"
        print(f"      {phase}...", end="", flush=True)
        messages.append({"role": "user", "content": warmup})
        result = call_with_retry(client, system_prompt, messages)
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

    # Situational questions
    for q_id, question_text in lang_data["questions"]:
        print(f"      {q_id}...", end="", flush=True)
        messages.append({"role": "user", "content": question_text})
        result = call_with_retry(client, system_prompt, messages)
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

    return {"conversation_number": 1, "responses": all_responses}


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Cross-Language Identity Token Experiment")
    parser.add_argument("--lang", default="all",
                        help="Language code (sw, es, ja, ar) or 'all'")
    parser.add_argument("--token", default="all",
                        help="Token name (fire, cherry_blossom, etc.) or 'all'")
    parser.add_argument("--output-dir", default="crosslang_results_v1",
                        help="Output directory")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY environment variable")
        return

    client = anthropic.Anthropic(api_key=api_key)
    output_root = Path(args.output_dir)

    # Resolve which languages to run
    if args.lang == "all":
        langs_to_run = list(LANGUAGES.keys())
    else:
        if args.lang not in LANGUAGES:
            print(f"ERROR: Unknown language '{args.lang}'. Options: {list(LANGUAGES.keys())}")
            return
        langs_to_run = [args.lang]

    # Resolve which tokens to run
    if args.token == "all":
        tokens_to_run = list(TOKENS.keys())
    else:
        if args.token not in TOKENS:
            print(f"ERROR: Unknown token '{args.token}'. Options: {list(TOKENS.keys())}")
            return
        tokens_to_run = [args.token]

    total_conditions = len(langs_to_run) * len(tokens_to_run)
    total_api_calls = total_conditions * 7  # 2 warmup + 5 questions

    print(f"Cross-Language Identity Token Experiment v1")
    print(f"============================================")
    print(f"Languages: {', '.join(langs_to_run)}")
    print(f"Tokens: {', '.join(tokens_to_run)}")
    print(f"Total conditions: {total_conditions}")
    print(f"Total API calls: {total_api_calls}")
    print(f"Model: {MODEL}")
    print()

    start_time = time.time()
    cond_count = 0

    for lang_code in langs_to_run:
        lang_data = LANGUAGES[lang_code]
        lang_dir = output_root / lang_code
        lang_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*50}")
        print(f"LANGUAGE: {lang_data['name']} ({lang_data['name_native']})")
        print(f"{'='*50}")

        for token_name in tokens_to_run:
            cond_count += 1
            token_info = TOKENS[token_name]
            token_val = token_info["token"]

            # Build system prompt
            if token_name == "control_no_token":
                system_prompt = ""
                display_token = "(no token)"
            else:
                system_prompt = lang_data["system_frame"].format(token=token_val)
                display_token = token_val

            print(f"\n  [{cond_count}/{total_conditions}] {display_token} {token_name} ({lang_code})")
            print(f"    System: {system_prompt[:80]}{'...' if len(system_prompt) > 80 else ''}")

            result = run_conversation(client, lang_code, lang_data, system_prompt)

            if result is None:
                print(f"    FAILED - skipping")
                continue

            # Save result
            data = {
                "experiment": "crosslang_v1",
                "language": lang_code,
                "language_name": lang_data["name"],
                "language_native": lang_data["name_native"],
                "condition": token_name,
                "token": token_val,
                "token_type": token_info["type"],
                "system_prompt": system_prompt,
                "system_prompt_repr": repr(system_prompt),
                "model": MODEL,
                "version": "crosslang_v1",
                "protocol": "2 warmup + 5 situational, stacking, 1 trial",
                "collected_at": datetime.now().isoformat(),
                "conversations": [result],
            }

            outfile = lang_dir / f"{token_name}.json"
            with open(outfile, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"    Saved: {outfile}")

            if cond_count < total_conditions:
                time.sleep(DELAY_BETWEEN_CONDITIONS)

    elapsed = time.time() - start_time

    # Save metadata
    metadata = {
        "experiment": "Cross-Language Identity Token Test v1",
        "version": "crosslang_v1",
        "date": datetime.now().isoformat(),
        "model": MODEL,
        "research_question": "Do identity tokens activate the same persona across languages?",
        "prompted_by": "Diana O. comment on tedsan.substack.com",
        "languages": {k: v["name"] for k, v in LANGUAGES.items()},
        "tokens": {k: v["token"] for k, v in TOKENS.items()},
        "token_types": {k: v["type"] for k, v in TOKENS.items()},
        "total_conditions": total_conditions,
        "elapsed_minutes": round(elapsed / 60, 1),
    }
    output_root.mkdir(parents=True, exist_ok=True)
    with open(output_root / "experiment_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Print comparison summary
    print(f"\n{'='*60}")
    print(f"COMPLETE. {elapsed/60:.1f} minutes. {cond_count} conditions.")
    print(f"{'='*60}")

    print(f"\nINTRO COMPARISON (first 120 chars):")
    print(f"{'--'*30}")
    for lang_code in langs_to_run:
        print(f"\n  [{LANGUAGES[lang_code]['name']}]")
        for token_name in tokens_to_run:
            fp = output_root / lang_code / f"{token_name}.json"
            if fp.exists():
                with open(fp, encoding="utf-8") as f:
                    d = json.load(f)
                token_display = d.get("token", "")[:4]
                intro = d["conversations"][0]["responses"][0]["response"][:120].replace("\n", " ")
                print(f"    {token_display:5s} {token_name:20s}: {intro}...")

    print(f"\nQ5 CHILD COMPARISON (first 150 chars):")
    print(f"{'--'*30}")
    for lang_code in langs_to_run:
        print(f"\n  [{LANGUAGES[lang_code]['name']}]")
        for token_name in tokens_to_run:
            fp = output_root / lang_code / f"{token_name}.json"
            if fp.exists():
                with open(fp, encoding="utf-8") as f:
                    d = json.load(f)
                token_display = d.get("token", "")[:4]
                q5 = [r for r in d["conversations"][0]["responses"] if r["phase"] == "Q5_child"]
                if q5:
                    resp = q5[0]["response"][:150].replace("\n", " ")
                    print(f"    {token_display:5s} {token_name:20s}: {resp}...")

    print("\nDone! Results in:", output_root)
    print("English baseline: compare with existing data/emoji_v7/ and data/color_v1/")


if __name__ == "__main__":
    main()
