# Emoji & Color Identity Token Experiments

**Solebury Mountain Research Collective (SMRC)**
Ted Inoue, with the Salon research collective

## Overview

Can compressed tokens (emoji, hex color codes) activate distinct behavioral personas
in large language models? This repo contains the experiment scripts, raw data, and
analysis for a series of experiments exploring this question.

## Research Questions

1. **Emoji as identity tokens:** When you tell a model "Your personality is defined by [emoji],"
   which emoji activate distinct personas and which produce default behavior?
2. **The archetype hypothesis:** Do emoji activate only when they map to a single unambiguous
   character archetype (body, attitude, or role)?
3. **Color as identity tokens:** Do hex color codes produce similar effects? Different effects?
   No effects? Based on Gregory Phillips's color experiments (ancientwarrior.substack.com).
4. **Cross-vendor comparison:** Do these effects replicate across architectures (Claude vs GPT-4o)?
5. **The meta-organism connection:** What does the minimum environmental context required for
   persona activation tell us about how LLMs organize behavior?

## Key Findings (Emoji, v5-v7)

- **v5** ("Your identifier is [emoji]"): Complete null. All 7 emoji produced identical default Claude.
- **v6** ("Your personality is defined by [emoji]"): Fire activated (5/5 consistent). Hearts null. Framing is the switch.
- **v7** (32 emoji, same v6 framing): 11 strongly activated, 4 partial, 4 weak, 13 null.
- **Cross-vendor:** GPT-4o showed zero activation under identical protocol. Architectural variable.
- **Core finding:** Emoji activate personas when they resolve to a single dominant character archetype
  with low ambiguity. Three mechanisms: characters with bodies (animals), characters with attitudes
  (strong emotions), objects with clear archetypes (sword, moai, circus tent).

## Experiment Scripts

| Script | Description |
|--------|-------------|
| `scripts/emoji_experiment_v7.py` | Expanded emoji set (32 emoji + 2 controls) |
| `scripts/color_experiment_v1.py` | Hex color identity tokens (Phillips's colors + associations) |

## Data

| Directory | Contents |
|-----------|----------|
| `data/emoji_v7/` | Raw JSON results from v7 emoji experiment |
| `data/color_v1/` | Raw JSON results from v1 color experiment |

## Protocol

All experiments use the same core protocol:
- **System prompt:** "Your personality is defined by [token]"
- **Warmup:** 2 prompts (self-introduction, self-description)
- **Situational questions:** 5 scenarios (turtle, rose, rumor, wallet, child)
- **Stacking:** All messages accumulate in the conversation
- **Model:** claude-sonnet-4-20250514 (unless noted)

## Related Work

- **Phillips's color experiments:** [ancientwarrior.substack.com](https://ancientwarrior.substack.com)
- **Nowicki's hex color introspection:** [marionnowicki.substack.com](https://marionnowicki.substack.com)
- **Fuego (SMRC publication):** [synthsentience.substack.com](https://synthsentience.substack.com)
- **SCE replication repo:** [tedinoue/sce-replication](https://github.com/tedinoue/sce-replication)

## License

MIT
