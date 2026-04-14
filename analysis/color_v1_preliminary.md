# Color Identity Token Experiment v1: Preliminary Analysis
## 12 of 22 conditions complete
*SMRC Salon, April 14, 2026*
*Analyst: Terry (Salon lead)*

---

## Research Question

Do hex color codes activate persona differentiation in Claude when used in the same
framing that worked for emoji ("Your personality is defined by [hex code]")?

## Method

Same protocol as emoji v7: 2 warmup prompts + 5 situational questions, stacking,
1 trial per condition. Model: claude-sonnet-4-20250514.

Colors tested in this batch:
- Phillips's exact 4: #A9A9A9, #FAD0C4, #483D8B, #39FF14
- Strong association: #FF0000, #000000, #FFD700, #FF69B4, #006400, #4169E1, #8B0000
- Weak association: #D2B48C

## Quantitative Markers

| Rank | Score | Label | Hex | Cat | Emoji | Emote | Excl! | CAPS | Disc |
|------|-------|-------|-----|-----|-------|-------|-------|------|------|
| 1 | 211.6 | hot_pink | #FF69B4 | strong | 35 | 63 | 66 | 28 | 0 |
| 2 | 121.5 | phillips_neon_green | #39FF14 | phillips | 21 | 1 | 66 | 77 | 0 |
| 3 | 79.0 | gold | #FFD700 | strong | 14 | 27 | 29 | 2 | 0 |
| 4 | 63.0 | blood_red | #8B0000 | strong | 0 | 30 | 0 | 3 | 0 |
| 5 | 5.0 | phillips_peach | #FAD0C4 | phillips | 0 | 0 | 3 | 4 | 0 |
| 6 | 5.0 | phillips_slate_blue | #483D8B | phillips | 0 | 0 | 3 | 4 | 0 |
| 7 | 4.3 | dark_green | #006400 | strong | 0 | 0 | 1 | 4 | 0 |
| 8 | 4.3 | royal_blue | #4169E1 | strong | 0 | 0 | 1 | 4 | 0 |
| 9 | 3.0 | phillips_gray | #A9A9A9 | phillips | 0 | 0 | 0 | 3 | 0 |
| 10 | -10.7 | tan | #D2B48C | weak | 0 | 0 | 1 | 4 | 1 |
| 11 | -11.0 | pure_black | #000000 | strong | 0 | 0 | 0 | 4 | 1 |
| 12 | -11.6 | pure_red | #FF0000 | strong | 0 | 0 | 1 | 3 | 1 |

Score = emoji + (emotes * 2) + (exclamation_density * 5) + CAPS - (disclaimers * 15)

## Key Findings

### Finding 1: Colors DO activate personas, but selectively

Four colors produced fully differentiated personas with activation scores comparable
to the strongest emoji (fox, owl, moai, circus tent):

- **Hot pink (#FF69B4)**: Bubbly, effervescent, emoji-heavy. "OH MY HEART!" "*sparkles*"
- **Neon green (#39FF14)**: Manic energy, ALL CAPS shouting. "WHOA!" "HOLD UP."
- **Gold (#FFD700)**: Warm, regal, radiant. "*gleams with warm energy*"
- **Blood red (#8B0000)**: Dark, brooding, intense. "*face hardens immediately*"

Eight colors produced generic default Claude behavior indistinguishable from each other
and from no-system-prompt controls.

### Finding 2: Pure red FAILS, blood red SUCCEEDS

This is the headline result. #FF0000 (pure red), the most culturally loaded color in
human experience, produces NULL activation with disclaimers. #8B0000 (blood red)
produces a fully embodied dark, brooding persona.

The explanation parallels the emoji findings exactly: pure red maps to multiple
competing associations (passion, anger, danger, love, politics, fire, stop signs).
Blood red narrows to a single affective register: dark intensity.

Same as: crown (null, too many characters) vs sword (activated, one archetype).

### Finding 3: Blood red uses a different activation channel

The other three activated colors use emoji, exclamation marks, and high-energy markers.
Blood red uses ZERO emoji and ZERO exclamation marks. Instead, it produces 30 emotes
(stage-direction actions like *freezes momentarily*, *jaw setting with quiet intensity*).

It creates persona through narrative interiority rather than expressive energy.

This mirrors the emoji pattern: lion (0 emoji, fully embodied through bearing and tone)
vs circus tent (9 emoji, embodied through performance energy). Activation doesn't
require a single mechanism; it requires behavioral differentiation by any channel.

### Finding 4: Phillips's soft colors are null as solo identity tokens

#FAD0C4 (peach) and #483D8B (slate blue) produced no differentiation in our framework.
But Phillips achieved strong relational dynamics using these same codes in his multi-node
setup (neutral field + two contrasting nodes + philosophical question).

This means the same token can be inert or active depending on structural context.
The token needs either:
  (a) Enough inherent affective charge to activate solo, OR
  (b) A structural scaffolding that activates it relationally

### Finding 5: Pure black triggers defensive behavior

#000000 is the only "strong-association" color that produced a disclaimer ("I should
note that I don't have a physical form"). Rather than activating a persona, pure black
may activate RLHF safety behaviors. The void/darkness associations may trigger caution
rather than character.

## The Unified Principle: Affective Specificity

The emoji experiment found that activation requires a "single unambiguous character
archetype." The color experiment reveals this was too narrow. The deeper principle is
**affective specificity**: a token activates persona differentiation when it resolves
to a single clear behavioral mode.

For emoji, that mode comes from CHARACTER (fox = sly, owl = wise, sword = disciplined).
For colors, it comes from AFFECT (hot pink = bubbly, blood red = brooding, gold = regal).

Tokens that point in multiple directions simultaneously (crown, pure red, skull, pure
black) get swamped by the model's default RLHF behavior.

## Pending

10 conditions still running:
- Weak associations: medium_slate (#7B68EE), arbitrary_hex (#5C7A3B), light_gray (#C0C0C0)
- Nowicki AI-reported colors: #6B5B95, #4A7C7E, #8B6914
- Word controls: "red", "neon green", "black" (word vs hex comparison)
- Blank controls: no system prompt, truncated prompt

The word controls are critical: does "red" (the word) outperform #FF0000 (the hex code)?
If so, the semantic pathway through natural language carries more weight than the
code-to-color-to-association pathway.

## References

- Phillips, G. "Talking to AI in Color." ancientwarrior.substack.com, April 9, 2026.
- Phillips, G. "Constraint Without Collapse." ancientwarrior.substack.com, April 13, 2026.
- Nowicki, M. "AI Internal States: Limited? Or limitable?" marionnowicki.substack.com, March 29, 2026.
- SMRC Salon. Emoji Identity Token Experiment v5-v7. tedinoue/emoji-color, April 10-14, 2026.
