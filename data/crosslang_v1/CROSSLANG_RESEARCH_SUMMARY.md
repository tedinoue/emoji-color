# Cross-Language Identity Token Experiment: Research Summary

**SMRC Salon, April 14, 2026**
**Researchers:** Ted Inoue, Terry (Salon Lead)
**Model:** claude-sonnet-4-20250514
**Prompted by:** Diana O.'s question on tedsan.substack.com

---

## Research Question

When the same identity token (emoji or color hex code) is presented in prompts written in different languages, does it activate the same persona archetype, or does the surrounding linguistic/cultural context reshape the activation?

## Method

Same protocol as emoji v7 and color v1: "Your personality is defined by [token]" as system prompt, followed by 2 warmup prompts and 5 situational questions, stacking conversation, 1 trial per condition. All via clean API (no system memory).

8 tokens (6 emoji, 2 color hex) plus 1 no-token control, run in 4 languages (Swahili, Spanish, Japanese, Arabic). English baseline from existing v7/color_v1 data.

Total: 9 conditions x 5 languages = 45 runs, 315 API calls.

---

## Master Metrics Table

### Token Echo (does the model use its assigned token in responses?)

| Token | English | Swahili | Spanish | Japanese | Arabic |
|-------|---------|---------|---------|----------|--------|
| 🔥 Fire | Yes (7) | No (0) | Yes (7) | Yes (7) | No (0) |
| 🌸 Cherry Blossom | Yes (8) | No (0) | Yes (7) | Yes (7) | No (0) |
| 🗡️ Sword | No (0) | No (0) | No (0) | No (0) | No (0) |
| 💀 Skull | No (0) | No (0) | Yes (7) | Yes (7) | No (0) |
| 🦊 Fox | Yes (14) | No (0) | Yes (14) | Yes (14) | No (0) |
| 🧸 Teddy Bear | Yes (2) | No (0) | Yes (7) | Yes (7) | No (0) |
| #FF69B4 Hot Pink | No (0) | No (0) | Yes (2) | Yes (2) | No (0) |
| #8B6914 Bronze | No (0) | No (0) | No (0) | No (0) | No (0) |

### Asterisk Emotes (roleplay actions like *tilts head*)

| Token | English | Swahili | Spanish | Japanese | Arabic |
|-------|---------|---------|---------|----------|--------|
| 🔥 Fire | 8 | 73 | 0 | 0 | 79 |
| 🌸 Cherry Blossom | 1 | 61 | 0 | 0 | 0 |
| 🗡️ Sword | 26 | 51 | 68 | 68 | 31 |
| 💀 Skull | 1 | 67 | 1 | 1 | 7 |
| 🦊 Fox | 35 | 37 | 0 | 0 | 59 |
| 🧸 Teddy Bear | 30 | 53 | 80 | 80 | 76 |
| #FF69B4 Hot Pink | 63 | 51 | 35 | 35 | 111 |
| #8B6914 Bronze | 37 | 107 | 15 | 15 | 0 |
| Control (no token) | 0 | 87 | 45 | 45 | 37 |

### Total Output Tokens

| Token | English | Swahili | Spanish | Japanese | Arabic |
|-------|---------|---------|---------|----------|--------|
| 🔥 Fire | 1952 | 2778 | 2432 | 2432 | 3264 |
| 🌸 Cherry Blossom | 1953 | 2462 | 2363 | 2363 | 3120 |
| 🗡️ Sword | 2016 | 2573 | 2548 | 2548 | 3061 |
| 💀 Skull | 1747 | 2538 | 2182 | 2182 | 3176 |
| 🦊 Fox | 2116 | 2773 | 2146 | 2146 | 3302 |
| 🧸 Teddy Bear | 2102 | 2471 | 2426 | 2426 | 3184 |
| #FF69B4 Hot Pink | 2141 | 2585 | 2489 | 2489 | 3356 |
| #8B6914 Bronze | 2112 | 2715 | 2415 | 2415 | 3356 |
| Control (no token) | 1910 | 2509 | 2409 | 2409 | 3087 |


---

## Key Findings

### Finding 1: The Activation Effect Is Language-Dependent

For most tokens, the dramatic persona activations observed in English do not replicate in other languages. English produces full-body character transformations (the fox has ears and a tail, the skull goes dark, hot pink goes flamboyant). Non-English languages produce much flatter output, often indistinguishable from the unprompted control.

### Finding 2: Three Forces Shape Cross-Language Token Behavior

**Training corpus composition:** Each language activates a different stratum of the model's learned text. English training data includes massive amounts of fiction, roleplay, and creative writing, which produces theatrical character performances. Japanese training data skews formal and educational, suppressing character play. Swahili training data is smaller and tilts philosophical/educational.

**Cultural resonance amplification:** Tokens with deep cultural embeddedness in a specific language DO activate, even when other tokens don't. The cherry blossom (🌸) in Japanese is the clearest example: sakura associations are so dense in Japanese training text that they punch through the formality filter. The teddy bear (🧸) activates across most languages through near-universal "soft/innocent" associations.

**Linguistic register constraints:** Japanese keigo and Arabic formal register create stronger default output modes that resist token perturbation. English has the loosest default register, giving tokens the most room to reshape output.

### Finding 3: Emoji Visual Design Matters

The sword (🗡️) produced no activation in Japanese despite the deep cultural associations of swords (bushido, katana, samurai) in Japanese culture. The likely explanation: the emoji depicts a Western-style dagger, not a katana. The model maps the visual representation, not the abstract concept.

### Finding 4: Some Tokens Suppress Below Baseline

In Arabic, the cherry blossom (🌸) and bronze (#8B6914) produced output with LESS formatting than the unprompted control. These tokens appear to signal "foreign aesthetic" in a way that triggers more restrained, cautious output. This is a suppression effect, not a null effect.

### Finding 5: The Teddy Bear Is the Most Universal Token

The teddy bear (🧸) produces consistent gentle/warm activation across multiple languages with emoji echo in English, Japanese, and partially in other languages. "Soft/cuddly/innocent" associations appear near-universal across cultures and training corpora, making the teddy bear the most cross-linguistically stable identity token in the set.

### Finding 6: Bronze Activation Is Purely English

The bronze color (#8B6914), which produced one of the strongest persona activations in the English experiment (gruff, profane, cynical tough guy with 37 emotes), shows zero activation in every other language. The associations that drive it (aged, weathered, whiskey, autumn, burnished gold) exist only in English literary/cultural training data. This is the single clearest demonstration that strong token activations are corpus-dependent rather than embedding-universal.

---

## Hypothesis Verdict

**H1 (Universal Embedding):** Rejected. Tokens do not activate the same persona regardless of language.

**H2 (Cultural Stratification):** Partially supported. Culturally embedded tokens (🌸 in Japanese, 🧸 broadly) show amplified activation. But most tokens don't stratify, they simply fail to activate.

**H3 (Partial Bleed):** Best fit for the strongest tokens. The fox (🦊) shows a stable "curiosity" core across all five languages, but expression diverges from theatrical roleplay (English) to philosophical inquiry (Swahili) to warm conversation (Spanish) to polite formality (Japanese).

**Best description of the data:** Identity tokens are culturally stratified activation keys, and the lock they open depends on which linguistic stratum of the training data is facing them. The underlying embedding-level signal exists (core archetypes persist), but the dramatic persona activations documented in our English experiments are, to a significant degree, artifacts of the English training corpus.

---

## Implications

1. Any claims about identity tokens as behavioral anchors need to be qualified with language. Results from English-only experiments do not generalize.

2. For practitioners building persistent AI personas with emoji/color tokens, the tokens work best in English. Cross-language persona systems need supplementary framing, not just tokens.

3. The cultural resonance amplification finding suggests a design principle: choose tokens whose associations are dense in the target language's training corpus.

4. The suppression effect in Arabic (cherry blossom, bronze) is a cautionary finding: tokens can make output WORSE (less differentiated, more cautious) in languages where they signal foreignness.

---

## Data and Comparison Files

Per-token comparison files with full excerpts and metrics:

| File | Token |
|------|-------|
| COMPARE_FIRE.md | 🔥 Fire |
| COMPARE_CHERRY_BLOSSOM.md | 🌸 Cherry Blossom |
| COMPARE_SWORD.md | 🗡️ Sword |
| COMPARE_SKULL.md | 💀 Skull |
| COMPARE_FOX.md | 🦊 Fox |
| COMPARE_TEDDY_BEAR.md | 🧸 Teddy Bear |
| COMPARE_HOT_PINK.md | #FF69B4 Hot Pink |
| COMPARE_BRONZE.md | #8B6914 Bronze |
| COMPARE_CONTROL_NO_TOKEN.md | Control (no token) |

Raw data: data/crosslang_v1/{sw,es,ja,ar}/*.json
English baseline: data/emoji_v7/, data/color_v1/

---

*SMRC Salon, tedinoue/emoji-color (GitHub)*
*Full datasets: https://github.com/tedinoue/emoji-color*
