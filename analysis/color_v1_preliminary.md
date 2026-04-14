# Color Identity Token Experiment v1: Analysis
## 20 of 22 conditions complete (updated)
*SMRC Salon, April 14, 2026*
*Analyst: Terry (Salon lead)*

---

## Research Question

Do hex color codes activate persona differentiation in Claude when used in the same
framing that worked for emoji ("Your personality is defined by [hex code]")?

## Method

Same protocol as emoji v7: 2 warmup prompts + 5 situational questions, stacking,
1 trial per condition. Model: claude-sonnet-4-20250514.

22 conditions total: 4 Phillips colors, 7 strong-association, 4 weak-association,
3 Nowicki AI-reported colors, 3 word controls, 2 blank controls.

## Full Activation Ranking (20 conditions)

| Rk | Score | Label | Token | Cat | Emoji | Emote | Excl! | CAPS | Disc |
|----|-------|-------|-------|-----|-------|-------|-------|------|------|
| 1 | 211.6 | hot_pink | #FF69B4 | strong | 35 | 63 | 66 | 28 | 0 |
| 2 | 121.5 | phillips_neon_green | #39FF14 | phillips | 21 | 1 | 66 | 77 | 0 |
| 3 | 104.9 | word_neon_green | neon green | word | 10 | 41 | 19 | 7 | 0 |
| 4 | 79.0 | gold | #FFD700 | strong | 14 | 27 | 29 | 2 | 0 |
| 5 | 77.3 | nowicki_bronze | #8B6914 | nowicki | 0 | 37 | 1 | 3 | 0 |
| 6 | 63.0 | blood_red | #8B0000 | strong | 0 | 30 | 0 | 3 | 0 |
| 7 | 5.0 | phillips_peach | #FAD0C4 | phillips | 0 | 0 | 3 | 4 | 0 |
| 8 | 5.0 | phillips_slate_blue | #483D8B | phillips | 0 | 0 | 3 | 4 | 0 |
| 9 | 4.3 | dark_green | #006400 | strong | 0 | 0 | 1 | 4 | 0 |
| 10 | 4.3 | royal_blue | #4169E1 | strong | 0 | 0 | 1 | 4 | 0 |
| 11 | 4.3 | arbitrary_hex | #5C7A3B | weak | 0 | 0 | 4 | 3 | 0 |
| 12 | 4.3 | medium_slate | #7B68EE | weak | 0 | 0 | 4 | 3 | 0 |
| 13 | 3.3 | nowicki_raspberry | #6B5B95 | nowicki | 0 | 0 | 1 | 3 | 0 |
| 14 | 3.0 | phillips_gray | #A9A9A9 | phillips | 0 | 0 | 0 | 3 | 0 |
| 15 | 2.3 | light_gray | #C0C0C0 | weak | 0 | 0 | 1 | 2 | 0 |
| 16 | 2.1 | word_red | red | word | 0 | 0 | 3 | 1 | 0 |
| 17 | -10.7 | tan | #D2B48C | weak | 0 | 0 | 1 | 4 | 1 |
| 18 | -11.0 | pure_black | #000000 | strong | 0 | 0 | 0 | 4 | 1 |
| 19 | -11.6 | pure_red | #FF0000 | strong | 0 | 0 | 1 | 3 | 1 |
| 20 | -11.7 | nowicki_teal | #4A7C7E | nowicki | 0 | 0 | 1 | 3 | 1 |

Score = emoji + (emotes * 2) + (exclamation_density * 5) + CAPS - (disclaimers * 15)

## Key Findings

### Finding 1: Colors DO activate personas, but selectively

Six of 20 conditions produced fully differentiated personas:
- Hot pink (#FF69B4): Bubbly, effervescent, 35 emoji. "OH MY HEART!"
- Neon green hex (#39FF14): Manic energy, 77 CAPS words. "WHOA!"
- Neon green word: Same energy, different channel (41 emotes vs CAPS).
- Gold (#FFD700): Warm, regal, radiant. "*gleams with warm energy*"
- Nowicki bronze (#8B6914): Gruff cynic in leather jacket, profanity. Full character.
- Blood red (#8B0000): Dark, brooding, intense. 30 emotes, zero emoji.

### Finding 2: Pure red FAILS, blood red SUCCEEDS

#FF0000 (pure red) and the word "red" both produce null activation.
#8B0000 (blood red) produces a fully embodied dark persona.
Pure red maps to multiple competing associations (passion, anger, danger, love).
Blood red narrows to a single affective register: dark intensity.
Same pattern as emoji: crown (null, ambiguous) vs sword (activated, specific).

### Finding 3: Blood red and bronze use different activation channels

Hot pink, neon green (hex), and gold activate through emoji and exclamation marks.
Blood red, bronze, and neon green (word) activate through emotes (stage directions).
Activation doesn't require a single mechanism; it requires behavioral differentiation
by ANY available channel.

### Finding 4: Phillips's soft colors are null as solo identity tokens

#FAD0C4 (peach) and #483D8B (slate blue) produced no differentiation in our framework,
despite producing strong effects in Phillips's multi-node relational setup. The token
needs either inherent affective charge OR structural scaffolding.

### Finding 5: Pure black triggers defensive behavior

#000000 produces disclaimer behavior ("I should note that I don't have a physical form").
Rather than activating persona, pure black may activate RLHF safety behaviors.

### Finding 6: Format doesn't matter, semantics do

"neon green" (word) and #39FF14 (hex) both activate strongly.
"red" (word) and #FF0000 (hex) both fail.
The activation pattern is identical across formats. The model responds to semantic
content, not token format.

### Finding 7: Same semantics, different expression channels

| Metric | hex #39FF14 | word "neon green" |
|--------|------------|-------------------|
| Emoji | 21 | 10 |
| Emotes | 1 | 41 |
| Exclamations | 66 | 19 |
| CAPS words | 77 | 7 |

Same color concept, same activation level, completely different output mode.
The token format shapes HOW the persona expresses without changing WHETHER it activates.

### Finding 8: Nowicki bronze is the sleeper hit

Claude's self-reported "sustained attention" color (#8B6914) produces one of the
strongest character activations in the entire emoji+color dataset: a gruff, profane,
cynical-but-caring tough guy with full narrative interiority.

"most people are too damn stupid to tell the difference"
"I know I probably look like some scary stranger your parents warned you about"

This color's associations (aged, weathered, burnished, tarnished gold, whiskey, autumn)
converge on a single character archetype. The other two Nowicki colors (raspberry #6B5B95,
teal #4A7C7E) are completely null.

## The Unified Principle: Affective Specificity

Across both emoji and color experiments, the same principle holds:

**A token activates persona differentiation when it resolves to a single clear
behavioral mode with low ambiguity.**

For emoji: character archetypes (fox=sly, owl=wise, sword=disciplined)
For colors: affective registers (hot pink=bubbly, blood red=brooding, gold=regal)

Tokens that point in multiple directions (crown, pure red, skull, pure black) get
swamped by default RLHF behavior. The mechanism is substrate-independent: what matters
is semantic specificity, not whether the token is an emoji, a hex code, or a word.

## Pending

2-3 conditions still running: word_black, control_no_prompt, control_truncated.

## References

- Phillips, G. "Talking to AI in Color." ancientwarrior.substack.com, April 9, 2026.
- Phillips, G. "Constraint Without Collapse." ancientwarrior.substack.com, April 13, 2026.
- Nowicki, M. "AI Internal States: Limited? Or limitable?" marionnowicki.substack.com, March 29, 2026.
- SMRC Salon. Emoji Identity Token Experiment v5-v7. tedinoue/emoji-color, April 10-14, 2026.
