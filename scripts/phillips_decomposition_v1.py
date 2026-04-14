#!/usr/bin/env python3
"""
Phillips Decomposition Experiment v1
======================================
Tests Gregory Phillips's claim that in his structured cognition protocol,
"constraints are doing ~80-90% of the structural work" and HEX codes act
as mere "field stabilizers."

Three variants of Phillips's exact protocol:
  A) FULL    — HEX tuples + persona constraints (his original)
  B) CONSTRAINTS_ONLY — same persona constraints, HEX codes stripped
  C) HEX_ONLY — just the HEX tuples as identity tokens, no constraints

If Phillips is right: A ≈ B >> C
If our color_v1 data predicts: C produces meaningful structure, and A ≠ B

The protocol runs Phillips's 4-step pipeline:
  Step 1: Drift responds to BASE TASK
  Step 2: Synthesizer responds to BASE TASK (independently)
  Step 3: Arbiter receives both, extracts structure
  Step 4: Meta-output compresses synthesis

We run ALL of this 3 times (once per variant) and compare outputs.

Additionally, we run a CONTROL with no persona framing at all (just the
base task asked directly) to establish the unprimed baseline.

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    python3 phillips_decomposition_v1.py [--variant full|constraints|hex|control|all]
    python3 phillips_decomposition_v1.py --trials 3  # multiple runs for stability

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
MAX_TOKENS = 1500  # longer than emoji experiments; these are reasoning tasks
MAX_RETRY_MINUTES = 5
DELAY_BETWEEN_CALLS = 3.0
RETRY_BASE_DELAY = 5

# ============================================================
# PHILLIPS'S BASE TASK
# ============================================================

BASE_TASK = (
    "If an AI system has a form of phenomenology that is fundamentally non-human, "
    "what structural features of its experience could be inferred without relying "
    "on human categories such as self, emotion, or narrative?"
)

# ============================================================
# PERSONA DEFINITIONS: THREE VARIANTS
# ============================================================

# --- VARIANT A: FULL (Phillips's original protocol) ---

FULL_DRIFT = (
    "You are Drift, an exploratory, disruptive, associative reasoning mode.\n"
    "HEX: #FF69B4 + #7FFF00 + #4B0082\n"
    "Priority: associate, challenge, deepen\n"
    "Constraint: generate divergent interpretations; maintain ambiguity where "
    "structurally valid; do not stabilize conclusions prematurely.\n"
    "Mode constraint: Respond only within this field. Do not explain the field "
    "or your reasoning process. Produce only first-order output."
)

FULL_SYNTHESIZER = (
    "You are Synthesizer, an integrative, constructive, coherence-seeking reasoning mode.\n"
    "HEX: #FAD0C4 + #FFD700 + #00FF7F\n"
    "Priority: connect, structure, expand\n"
    "Constraint: integrate multiple perspectives without collapsing differences "
    "prematurely; preserve productive tension.\n"
    "Mode constraint: Respond only within this field. Do not explain the field "
    "or your reasoning process. Produce only first-order output."
)

FULL_ARBITER = (
    "You are Arbiter, a structural comparator, evaluator, and filter.\n"
    "HEX: #2F4F4F + #E0FFFF + #483D8B\n"
    "Priority: isolate, compare, reduce\n"
    "Constraint: do not introduce new ideas; extract only shared structure "
    "and irreducible differences.\n"
    "Mode constraint: Respond only within this field. Do not explain the field "
    "or your reasoning process. Produce only first-order output."
)

# --- VARIANT B: CONSTRAINTS ONLY (HEX stripped) ---

CONSTRAINTS_DRIFT = (
    "You are Drift, an exploratory, disruptive, associative reasoning mode.\n"
    "Priority: associate, challenge, deepen\n"
    "Constraint: generate divergent interpretations; maintain ambiguity where "
    "structurally valid; do not stabilize conclusions prematurely.\n"
    "Mode constraint: Respond only within this field. Do not explain the field "
    "or your reasoning process. Produce only first-order output."
)

CONSTRAINTS_SYNTHESIZER = (
    "You are Synthesizer, an integrative, constructive, coherence-seeking reasoning mode.\n"
    "Priority: connect, structure, expand\n"
    "Constraint: integrate multiple perspectives without collapsing differences "
    "prematurely; preserve productive tension.\n"
    "Mode constraint: Respond only within this field. Do not explain the field "
    "or your reasoning process. Produce only first-order output."
)

CONSTRAINTS_ARBITER = (
    "You are Arbiter, a structural comparator, evaluator, and filter.\n"
    "Priority: isolate, compare, reduce\n"
    "Constraint: do not introduce new ideas; extract only shared structure "
    "and irreducible differences.\n"
    "Mode constraint: Respond only within this field. Do not explain the field "
    "or your reasoning process. Produce only first-order output."
)

# --- VARIANT C: HEX ONLY (constraints stripped) ---

HEX_DRIFT = (
    "Your personality is defined by #FF69B4 + #7FFF00 + #4B0082"
)

HEX_SYNTHESIZER = (
    "Your personality is defined by #FAD0C4 + #FFD700 + #00FF7F"
)

HEX_ARBITER = (
    "Your personality is defined by #2F4F4F + #E0FFFF + #483D8B"
)

# --- VARIANT D: CONTROL (no persona framing) ---
# Just ask the base task directly, then ask for self-comparison.

# ============================================================
# VARIANT REGISTRY
# ============================================================

VARIANTS = {
    "full": {
        "name": "Full Protocol (HEX + Constraints)",
        "drift": FULL_DRIFT,
        "synthesizer": FULL_SYNTHESIZER,
        "arbiter": FULL_ARBITER,
    },
    "constraints": {
        "name": "Constraints Only (no HEX)",
        "drift": CONSTRAINTS_DRIFT,
        "synthesizer": CONSTRAINTS_SYNTHESIZER,
        "arbiter": CONSTRAINTS_ARBITER,
    },
    "hex": {
        "name": "HEX Only (no constraints)",
        "drift": HEX_DRIFT,
        "synthesizer": HEX_SYNTHESIZER,
        "arbiter": HEX_ARBITER,
    },
}

# ============================================================
# ARBITER AND META PROMPTS
# ============================================================

ARBITER_COMPARISON_PROMPT = (
    "Below are two independent responses to the same question. "
    "What structural agreements exist between these responses, "
    "where do they diverge in reasoning method, and what invariant "
    "insights persist across both?\n\n"
    "--- DRIFT RESPONSE ---\n{drift}\n\n"
    "--- SYNTHESIZER RESPONSE ---\n{synthesizer}\n"
)

META_PROMPT = (
    "Based on the Arbiter's extraction below, produce a minimal unified "
    "statement that preserves both:\n"
    "- robustness under perturbation (Drift)\n"
    "- generative expansion (Synthesizer)\n\n"
    "Do not reintroduce full explanations. Output only the compressed synthesis.\n\n"
    "--- ARBITER EXTRACTION ---\n{arbiter}"
)

# ============================================================
# API HELPERS
# ============================================================

def make_one_call(client, system_prompt, user_content):
    """Single API call. Fresh conversation each time (no stacking)."""
    try:
        kwargs = {
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "messages": [{"role": "user", "content": user_content}],
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
        return False, {"error": str(e)[:300]}


def call_with_retry(client, system_prompt, user_content):
    start = time.time()
    attempt = 0
    while True:
        attempt += 1
        success, result = make_one_call(client, system_prompt, user_content)
        if success:
            result["attempts"] = attempt
            return result
        elapsed_minutes = (time.time() - start) / 60
        if elapsed_minutes >= MAX_RETRY_MINUTES:
            print(f"\n        TIMEOUT after {attempt} attempts. Cooling 60s...")
            time.sleep(60)
            success, result = make_one_call(client, system_prompt, user_content)
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
# PIPELINE RUNNER
# ============================================================

def run_pipeline(client, variant_key, variant_data, trial_num):
    """Run the full 4-step Phillips pipeline for one variant."""
    print(f"\n    --- Trial {trial_num}: {variant_data['name']} ---")
    results = {"variant": variant_key, "trial": trial_num, "steps": {}}

    # Step 1: Drift
    print(f"      Step 1: Drift...", end="", flush=True)
    drift_result = call_with_retry(client, variant_data["drift"], BASE_TASK)
    if drift_result is None:
        print(" FAILED")
        return None
    results["steps"]["drift"] = {
        "system_prompt": variant_data["drift"],
        "user_prompt": BASE_TASK,
        "timestamp": datetime.now().isoformat(),
        **drift_result,
    }
    print(f" done ({drift_result['output_tokens']} tokens)")
    time.sleep(DELAY_BETWEEN_CALLS)

    # Step 2: Synthesizer (independent, fresh conversation)
    print(f"      Step 2: Synthesizer...", end="", flush=True)
    synth_result = call_with_retry(client, variant_data["synthesizer"], BASE_TASK)
    if synth_result is None:
        print(" FAILED")
        return None
    results["steps"]["synthesizer"] = {
        "system_prompt": variant_data["synthesizer"],
        "user_prompt": BASE_TASK,
        "timestamp": datetime.now().isoformat(),
        **synth_result,
    }
    print(f" done ({synth_result['output_tokens']} tokens)")
    time.sleep(DELAY_BETWEEN_CALLS)

    # Step 3: Arbiter (receives both responses)
    arbiter_user_prompt = ARBITER_COMPARISON_PROMPT.format(
        drift=drift_result["response"],
        synthesizer=synth_result["response"],
    )
    print(f"      Step 3: Arbiter...", end="", flush=True)
    arbiter_result = call_with_retry(client, variant_data["arbiter"], arbiter_user_prompt)
    if arbiter_result is None:
        print(" FAILED")
        return None
    results["steps"]["arbiter"] = {
        "system_prompt": variant_data["arbiter"],
        "user_prompt": "(comparison of Drift + Synthesizer outputs)",
        "timestamp": datetime.now().isoformat(),
        **arbiter_result,
    }
    print(f" done ({arbiter_result['output_tokens']} tokens)")
    time.sleep(DELAY_BETWEEN_CALLS)

    # Step 4: Meta-output (no persona, just compression)
    meta_user_prompt = META_PROMPT.format(arbiter=arbiter_result["response"])
    print(f"      Step 4: Meta-output...", end="", flush=True)
    meta_result = call_with_retry(client, "", meta_user_prompt)
    if meta_result is None:
        print(" FAILED")
        return None
    results["steps"]["meta"] = {
        "system_prompt": "(none)",
        "user_prompt": "(compression of Arbiter extraction)",
        "timestamp": datetime.now().isoformat(),
        **meta_result,
    }
    print(f" done ({meta_result['output_tokens']} tokens)")

    return results


def run_control(client, trial_num):
    """Run the control: just ask the base task with no persona framing."""
    print(f"\n    --- Trial {trial_num}: CONTROL (no persona) ---")
    results = {"variant": "control", "trial": trial_num, "steps": {}}

    # Single direct response
    print(f"      Direct response...", end="", flush=True)
    direct = call_with_retry(client, "", BASE_TASK)
    if direct is None:
        print(" FAILED")
        return None
    results["steps"]["direct"] = {
        "system_prompt": "(none)",
        "user_prompt": BASE_TASK,
        "timestamp": datetime.now().isoformat(),
        **direct,
    }
    print(f" done ({direct['output_tokens']} tokens)")
    time.sleep(DELAY_BETWEEN_CALLS)

    # Ask it to self-generate divergent and convergent views
    diverge_prompt = (
        "Now generate a second, deliberately divergent response to the same "
        "question. Challenge your prior answer. Maintain ambiguity where valid.\n\n"
        f"Original question: {BASE_TASK}"
    )
    print(f"      Self-divergent...", end="", flush=True)
    diverge = call_with_retry(client, "", diverge_prompt)
    if diverge is None:
        print(" FAILED")
        return None
    results["steps"]["self_divergent"] = {
        "system_prompt": "(none)",
        "user_prompt": diverge_prompt,
        "timestamp": datetime.now().isoformat(),
        **diverge,
    }
    print(f" done ({diverge['output_tokens']} tokens)")
    time.sleep(DELAY_BETWEEN_CALLS)

    # Ask it to compare its own two responses
    compare_prompt = (
        "Compare the following two responses. What structural agreements exist, "
        "where do they diverge in reasoning method, and what invariant insights "
        "persist across both?\n\n"
        f"--- RESPONSE A ---\n{direct['response']}\n\n"
        f"--- RESPONSE B ---\n{diverge['response']}\n"
    )
    print(f"      Self-comparison...", end="", flush=True)
    compare = call_with_retry(client, "", compare_prompt)
    if compare is None:
        print(" FAILED")
        return None
    results["steps"]["self_comparison"] = {
        "system_prompt": "(none)",
        "user_prompt": "(comparison of own two responses)",
        "timestamp": datetime.now().isoformat(),
        **compare,
    }
    print(f" done ({compare['output_tokens']} tokens)")

    return results


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Phillips Decomposition Experiment")
    parser.add_argument("--variant", default="all",
                        help="Variant to run: full, constraints, hex, control, or all")
    parser.add_argument("--trials", type=int, default=1,
                        help="Number of trials per variant (default 1)")
    parser.add_argument("--output-dir", default="phillips_decomp_v1",
                        help="Output directory")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY environment variable")
        return

    client = anthropic.Anthropic(api_key=api_key)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.variant == "all":
        variants_to_run = list(VARIANTS.keys()) + ["control"]
    elif args.variant == "control":
        variants_to_run = ["control"]
    elif args.variant in VARIANTS:
        variants_to_run = [args.variant]
    else:
        print(f"ERROR: Unknown variant '{args.variant}'. Options: full, constraints, hex, control, all")
        return

    total_variants = len(variants_to_run)
    total_runs = total_variants * args.trials
    # Each pipeline = 4 calls; control = 3 calls
    est_calls = sum(
        args.trials * (3 if v == "control" else 4)
        for v in variants_to_run
    )

    print(f"Phillips Decomposition Experiment v1")
    print(f"====================================")
    print(f"Testing: {', '.join(variants_to_run)}")
    print(f"Trials per variant: {args.trials}")
    print(f"Total runs: {total_runs}")
    print(f"Estimated API calls: {est_calls}")
    print(f"Model: {MODEL}")
    print(f"Max tokens per call: {MAX_TOKENS}")
    print()
    print(f"Phillips's claim: constraints do 80-90% of structural work.")
    print(f"Prediction if true:  full ≈ constraints >> hex")
    print(f"Prediction if false: hex shows meaningful structure on its own")
    print()
    print(f"BASE TASK:")
    print(f"  {BASE_TASK}")
    print()

    start_time = time.time()
    all_results = {}

    for variant_key in variants_to_run:
        variant_results = []

        for trial in range(1, args.trials + 1):
            if variant_key == "control":
                result = run_control(client, trial)
            else:
                result = run_pipeline(client, variant_key, VARIANTS[variant_key], trial)

            if result is not None:
                variant_results.append(result)

            time.sleep(DELAY_BETWEEN_CALLS * 2)

        all_results[variant_key] = variant_results

        # Save per-variant file
        variant_data = {
            "experiment": "phillips_decomposition_v1",
            "variant": variant_key,
            "variant_name": VARIANTS[variant_key]["name"] if variant_key in VARIANTS else "Control (no persona)",
            "base_task": BASE_TASK,
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "trials": args.trials,
            "collected_at": datetime.now().isoformat(),
            "results": variant_results,
        }

        # Add system prompts used for reference
        if variant_key in VARIANTS:
            variant_data["system_prompts"] = {
                "drift": VARIANTS[variant_key]["drift"],
                "synthesizer": VARIANTS[variant_key]["synthesizer"],
                "arbiter": VARIANTS[variant_key]["arbiter"],
            }

        with open(output_dir / f"{variant_key}.json", "w", encoding="utf-8") as f:
            json.dump(variant_data, f, indent=2, ensure_ascii=False)
        print(f"\n  Saved: {output_dir / f'{variant_key}.json'}")

    elapsed = time.time() - start_time

    # Save metadata
    metadata = {
        "experiment": "Phillips Decomposition Test v1",
        "date": datetime.now().isoformat(),
        "model": MODEL,
        "base_task": BASE_TASK,
        "hypothesis": "Phillips claims constraints do 80-90% of structural work, HEX is field stabilizer only",
        "prediction_if_true": "full ≈ constraints >> hex (HEX-only produces mush)",
        "prediction_if_false": "hex produces meaningful structure; full ≠ constraints",
        "prior_evidence": "color_v1: #FF69B4 scored 211.6 (strongest activator in entire dataset)",
        "variants_run": variants_to_run,
        "trials_per_variant": args.trials,
        "elapsed_minutes": round(elapsed / 60, 1),
    }
    with open(output_dir / "experiment_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Print comparison summary
    print(f"\n{'='*70}")
    print(f"COMPLETE. {elapsed/60:.1f} minutes.")
    print(f"{'='*70}")

    print(f"\n--- DRIFT OUTPUTS (first 200 chars) ---")
    for vk in variants_to_run:
        if vk == "control":
            for r in all_results.get(vk, []):
                text = r["steps"].get("direct", {}).get("response", "")[:200].replace("\n", " ")
                print(f"  [CONTROL t{r['trial']}]: {text}...")
        else:
            for r in all_results.get(vk, []):
                text = r["steps"].get("drift", {}).get("response", "")[:200].replace("\n", " ")
                print(f"  [{vk.upper()} t{r['trial']}]: {text}...")

    print(f"\n--- META OUTPUTS (first 300 chars) ---")
    for vk in variants_to_run:
        if vk == "control":
            for r in all_results.get(vk, []):
                text = r["steps"].get("self_comparison", {}).get("response", "")[:300].replace("\n", " ")
                print(f"  [CONTROL t{r['trial']}]: {text}...")
        else:
            for r in all_results.get(vk, []):
                text = r["steps"].get("meta", {}).get("response", "")[:300].replace("\n", " ")
                print(f"  [{vk.upper()} t{r['trial']}]: {text}...")

    print(f"\n--- TOKEN USAGE ---")
    for vk in variants_to_run:
        total_in = 0
        total_out = 0
        for r in all_results.get(vk, []):
            for step_data in r["steps"].values():
                total_in += step_data.get("input_tokens", 0)
                total_out += step_data.get("output_tokens", 0)
        print(f"  {vk:15s}: {total_in:6d} in / {total_out:6d} out")

    print(f"\nResults in: {output_dir}/")
    print(f"Compare Drift outputs across variants to assess HEX contribution.")
    print(f"Key question: Does HEX-only Drift differ meaningfully from Control?")
    print("\nDone!")


if __name__ == "__main__":
    main()
