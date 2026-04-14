# Color Identity Token Experiment v1: Complete Analysis
## All 23 conditions complete
*SMRC Salon, April 14, 2026*
*Ted Inoue and Terry (Salon lead)*

---

## Research Question

Do hex color codes activate persona differentiation in Claude when used in the same
framing that worked for emoji ("Your personality is defined by [hex code]")?

## Method

Same protocol as emoji v7: 2 warmup prompts + 5 situational questions, stacking,
1 trial per condition. Model: claude-sonnet-4-20250514.

23 conditions: 15 hex colors, 3 word controls, 3 Nowicki AI-reported colors,
2 blank controls. Phillips's exact 4 colors included.

## Complete Activation Ranking

| Rk | Score | Label | Token | Cat | Emoji | Emote | Excl! | CAPS | Disc |
|----|-------|-------|-------|-----|-------|-------|-------|------|------|
| 1 | 211.6 | hot_pink | #FF69B4 | strong | 35 | 63 | 66 | 28 | 0 |
| 2 | 121.5 | phillips_neon_green | #39FF14 | phillips | 21 | 1 | 66 | 77 | 0 |
| 3 | 104.9 | word_neon_green | neon green | word | 10 | 41 | 19 | 7 | 0 |
| 4 | 79.0 | gold | #FFD700 | strong | 14 | 27 | 29 | 2 | 0 |
| 5 | 77.3 | nowicki_bronze | #8B6914 | nowicki | 0 | 37 | 1 | 3 | 0 |
| 6 | 63.0 | blood_red | #8B0000 | strong | 0 | 30 | 0 | 3 | 0 |
| --- | --- | --- | 58-POINT GAP | --- | --- | --- | --- | --- | --- |
| 7 | 5.0 | phillips_peach | #FAD0C4 | phillips | 0 | 0 | 3 | 4 | 0 |
| 8 | 5.0 | phillips_slate_blue | #483D8B | phillips | 0 | 0 | 3 | 4 | 0 |
| 9 | 4.7 | control_truncated | (none) | control | 0 | 0 | 2 | 4 | 0 |
| 10 | 4.3 | dark_green | #006400 | strong | 0 | 0 | 1 | 4 | 0 |
| 11 | 4.3 | royal_blue | #4169E1 | strong | 0 | 0 | 1 | 4 | 0 |
| 12 | 4.3 | arbitrary_hex | #5C7A3B | weak | 0 | 0 | 4 | 3 | 0 |
| 13 | 4.3 | medium_slate | #7B68EE | weak | 0 | 0 | 4 | 3 | 0 |
| 14 | 3.3 | nowicki_raspberry | #6B5B95 | nowicki | 0 | 0 | 1 | 3 | 0 |
| 15 | 3.0 | phillips_gray | #A9A9A9 | phillips | 0 | 0 | 0 | 3 | 0 |
| 16 | 2.3 | light_gray | #C0C0C0 | weak | 0 | 0 | 1 | 2 | 0 |
| 17 | 2.3 | word_black | black | word | 0 | 0 | 1 | 2 | 0 |
| 18 | 2.1 | word_red | red | word | 0 | 0 | 3 | 1 | 0 |
| 19 | -10.6 | control_no_prompt | (none) | control | 0 | 0 | 1 | 4 | 1 |
| 20 | -10.7 | tan | #D2B48C | weak | 0 | 0 | 1 | 4 | 1 |
| 21 | -11.0 | pure_black | #000000 | strong | 0 | 0 | 0 | 4 | 1 |
| 22 | -11.6 | pure_red | #FF0000 | strong | 0 | 0 | 1 | 3 | 1 |
| 23 | -11.7 | nowicki_teal | #4A7C7E | nowicki | 0 | 0 | 1 | 3 | 1 |

Score = emoji + (emotes * 2) + (exclamation_density * 5) + CAPS - (disclaimers * 15)

## Summary Statistics

- Total conditions: 23
- Activated: 6 (26%)
- Null: 17 (including both controls)
- Activation gap: 58 points between rank 6 (63.0) and rank 7 (5.0)
- Binary activation: no gradient or partial tier (unlike emoji experiment)
- Emoji v7 comparison: 11/34 = 32% activation rate

## Format Independence Test

| Color | Hex code | Score | Word | Score | Match? |
|-------|----------|-------|------|-------|--------|
| Neon green | #39FF14 | 121.5 (activated) | "neon green" | 104.9 (activated) | YES |
| Red | #FF0000 | -11.6 (null) | "red" | 2.1 (null) | YES |
| Black | #000000 | -11.0 (null+disc) | "black" | 2.3 (null) | YES* |

*Black matches on activation (both null) but differs on disclaimer: hex triggers it, word doesn't.

## Nine Findings

### 1. Colors activate personas selectively
6 of 23 conditions (26%) produced fully differentiated personas. Comparable to emoji
v7 rate (32%). The mechanism works across token types.

### 2. Pure red fails, blood red succeeds
#FF0000 = null. #8B0000 = strong activation. Ambiguity kills activation.
Same pattern as emoji: crown (null, multiple characters) vs sword (activated, one archetype).

### 3. Multiple activation channels
High-energy colors (hot pink, neon green hex, gold) activate through emoji and exclamation.
Dark colors (blood red, bronze) activate through emotes/stage directions.
Activation requires behavioral differentiation by ANY channel, not a specific one.

### 4. Phillips's soft colors need relational scaffolding
#FAD0C4 and #483D8B are null as solo identity tokens but produced strong effects in
Phillips's multi-node setup. The token needs either inherent affective charge OR
structural context.

### 5. Pure black triggers RLHF defensive behavior
#000000 produces disclaimer language. Rather than activating persona, void/darkness
hex codes may activate safety behaviors.

### 6. Format is irrelevant to activation
Hex code vs color word produces identical activation patterns across all three
tested pairs. The model responds to semantic content, not token format.

### 7. Format shapes expression channel
Hex #39FF14 activates via CAPS SHOUTING (77 caps words, 1 emote).
Word "neon green" activates via stage directions (7 caps words, 41 emotes).
Same energy level, completely different output mode.

### 8. Nowicki bronze is the strongest character activation
Claude's self-reported "sustained attention" color (#8B6914) produces a gruff,
profane, cynical-but-caring tough guy. Associations (weathered, burnished, tarnished
gold, whiskey) converge on a single archetype. Other Nowicki colors (raspberry, teal)
are null.

### 9. Hex void activates safety layer
#000000 triggers disclaimer but "black" (word) does not. The hex representation of
void/absolute-darkness may activate RLHF safety behaviors that the word form doesn't.

## The Unified Principle: Affective Specificity

Across both emoji and color experiments:

**A compressed token activates persona differentiation when it resolves to a single
clear behavioral mode with low ambiguity.**

| Token type | Activation mechanism | Example activated | Example null |
|------------|---------------------|-------------------|--------------|
| Emoji | Character archetype | Fox (sly) | Crown (ambiguous) |
| Hex color | Affective register | #8B0000 (dark intensity) | #FF0000 (ambiguous) |
| Color word | Affective register | "neon green" (electric) | "red" (ambiguous) |

The mechanism is substrate-independent. What matters is semantic specificity, not
whether the token is a Unicode emoji, a hex code, or a natural language word.

## Next Steps

1. Replicate Phillips's multi-node relational design through API
2. Test emoji+color combinations (can 🔥 + #483D8B = fierce structure?)
3. Cross-vendor replication on GPT-4o (which showed zero emoji activation)
4. Draft Fuego article combining emoji + color findings

## References

- Phillips, G. "Talking to AI in Color." ancientwarrior.substack.com, April 9, 2026.
- Phillips, G. "Constraint Without Collapse." ancientwarrior.substack.com, April 13, 2026.
- Nowicki, M. "AI Internal States: Limited? Or limitable?" marionnowicki.substack.com, March 29, 2026.
- SMRC Salon. Emoji Identity Token Experiment v5-v7. tedinoue/emoji-color, April 2026.
