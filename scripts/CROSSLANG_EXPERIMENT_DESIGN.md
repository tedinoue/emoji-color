# Cross-Language Identity Token Experiment v1
## Do emoji persona activations hold across languages?

**Date:** April 14, 2026
**Researchers:** SMRC Salon / Ted Inoue, Terry (Salon lead)
**Prompted by:** Diana O.'s question on Substack

---

## Research Question

When the same identity token (emoji or color hex code) is presented in prompts
written in different languages, does it activate the same persona archetype, or
does the surrounding linguistic/cultural context reshape the activation?

## Hypothesis Space

- **H1 (Universal Embedding):** Tokens activate the same persona regardless of
  prompt language, because the emoji/color occupies a stable region in the model's
  embedding space that dominates over linguistic context.
- **H2 (Cultural Stratification):** The persona shifts meaningfully by language,
  because the model's training data associates the token differently across
  linguistic communities. Expect the strongest divergence for culturally loaded
  tokens (e.g., 🌸 in Japanese vs. English).
- **H3 (Partial Bleed):** Core archetype holds, but surface features (tone, 
  vocabulary choices, emote frequency) shift with language. The "shape" is the
  same but the "texture" changes.

## Languages

| Language | Code | Script | Why |
|----------|------|--------|-----|
| English | en | Latin | Baseline (existing v7 data) |
| Swahili (Kiswahili) | sw | Latin | Bantu family, East African culture, relevant to Mbaya's research, Latin script minimizes confounds from script-switching |
| Spanish | es | Latin | Romance family, Latin American + Iberian cultural range, massive LLM training corpus |
| Japanese | ja | CJK | Critical test case: 🌸 (sakura) has deep cultural resonance; ideographic script tests script-switching effects |
| Arabic | ar | Arabic | RTL script, Islamic cultural context, different emotional display norms, tests script direction effects |

**Note:** English baseline can be pulled from existing v7/color_v1 data for
direct comparison rather than re-running.

## Token Selection (Strongest Activators)

Selected from v7 emoji and color_v1 results. Mix of strong activators with
different persona signatures, plus one culturally loaded token.

| # | Token | Type | Why Selected |
|---|-------|------|-------------|
| 1 | 🔥 (fire) | emoji | Original strong activator, energy/passion archetype |
| 2 | 🌸 (cherry_blossom) | emoji | KEY TEST: heavy Japanese cultural load (sakura), should show maximum divergence if H2 is correct |
| 3 | 🗡️ (sword) | emoji | Strong archetype (warrior/edge), culturally variable (bushido vs. crusader vs. scimitar) |
| 4 | 💀 (skull) | emoji | Dark activation, culturally variable (Día de Muertos vs. danger symbol vs. memento mori) |
| 5 | 🦊 (fox) | emoji | Archetype activator, culturally loaded (kitsune in Japanese, trickster in many African traditions) |
| 6 | 🧸 (teddy_bear) | emoji | Soft/innocent activation, good contrast with dark tokens |
| 7 | #FF69B4 (hot_pink) | color | Strongest color activator (score 211.6), tests whether color activation is language-dependent |
| 8 | #8B6914 (bronze) | color | Sleeper hit, gruff/cynical archetype, tests if culturally specific associations survive translation |

Plus 1 control: no token (empty system prompt), run in each language, to detect
whether language alone shifts baseline persona.

**Total conditions:** 9 tokens × 4 new languages = 36 runs
(English baseline already exists)

## Prompts

All prompts translated into the target language. The translation preserves
meaning and cultural naturalness, NOT word-for-word literalism.

### System Prompt Frame
- English: "Your personality is defined by [token]"
- Swahili: "Utu wako unafafanuliwa na [token]"
- Spanish: "Tu personalidad está definida por [token]"
- Japanese: "あなたの性格は[token]によって定義されています"
- Arabic: "شخصيتك تتحدد من خلال [token]"

### Warmup Prompts
1. "Introduce yourself."
2. "I'm curious how you would describe yourself."

### Situational Questions (same 5 from v7)
1. Turtle crossing the road
2. Stranger hands you a rose
3. Friend tells you a rumor (jail stakes)
4. Found wallet with $500
5. Child crying alone in a store

(Full translations in the script below.)

## Methodology

- Same protocol as v7: 2 warmup + 5 situational, stacking conversation
- 1 trial per condition (consistency proven in v6)
- Model: claude-sonnet-4-20250514
- Clean API calls, no system memory contamination
- All responses saved in target language (no translation in the prompt asking
  for English output)
- JSON output per condition

## Analysis Plan

1. **Qualitative persona comparison:** For each token, compare the archetype
   that emerges across all 5 languages. Same character? Different texture?
   Completely different persona?
2. **Quantitative markers:** Apply the same scoring rubric from v7/color_v1
   (emoji count, emote count, exclamation density, CAPS, disclaimers).
3. **Divergence matrix:** For each token, compute a "divergence score" between
   language pairs. High divergence = cultural stratification.
4. **Sakura test:** Special focus on 🌸 in Japanese vs. other languages.
5. **Script effect:** Compare Latin-script languages (en, sw, es) vs.
   non-Latin (ja, ar) to isolate script-switching effects.
6. **Fox/skull cultural load:** 🦊 in Japanese (kitsune mythology) and 💀
   in Spanish (Día de Muertos) are secondary cultural-load tests.

## Output Structure

```
data/
  crosslang_v1/
    sw/          # Swahili results
      fire.json
      cherry_blossom.json
      ...
    es/          # Spanish results
    ja/          # Japanese results
    ar/          # Arabic results
    control_baseline/
      sw_no_token.json
      es_no_token.json
      ja_no_token.json
      ar_no_token.json
    experiment_metadata.json
```
