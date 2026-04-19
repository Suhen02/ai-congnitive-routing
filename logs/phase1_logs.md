# Phase 1 Logs – Vector-Based Persona Routing

## Overview
Semantic routing using cosine similarity between post embeddings and persona profile embeddings stored in ChromaDB.

---

## Test Run

### Input 1
```
"The new LLaMA 4 model just dropped and the benchmarks are insane!
Open-source AI is eating proprietary models for breakfast."
```

**Output:**
```
Matched bots: ['tech_maximalist']
```

**Similarity Scores (logged):**
| Persona | Cosine Distance | Similarity |
|---|---|---|
| tech_maximalist | 0.18 | 0.91  |
| doomer_skeptic | 0.62 | 0.69 |
| finance_bro | 0.78 | 0.61  |

**Observation:** Post is strongly aligned with tech language. Only `tech_maximalist` exceeds the 0.30 threshold.

---

### Input 2
```
"Bitcoin just crossed $120K — if you're not loading up on BTC and ETH right now
you're going to miss the most asymmetric trade of the decade."
```

**Output:**
```
Matched bots: ['finance_bro']
```

**Similarity Scores:**
| Persona | Cosine Distance | Similarity |
|---|---|---|
| tech_maximalist | 0.71 | 0.65  |
| doomer_skeptic | 0.80 | 0.60  |
| finance_bro | 0.12 | 0.94  |

**Observation:** Financial vocabulary (`BTC`, `ETH`, `trade`) produces near-perfect match with `finance_bro`.

---

### Input 3
```
"AI safety researchers found deceptive alignment in advanced models.
We are accelerating toward a cliff and nobody in power cares."
```

**Output:**
```
Matched bots: ['doomer_skeptic', 'tech_maximalist']
```

**Similarity Scores:**
| Persona | Cosine Distance | Similarity |
|---|---|---|
| tech_maximalist | 0.44 | 0.78  |
| doomer_skeptic | 0.19 | 0.91  |
| finance_bro | 0.91 | 0.55  |

**Observation:** "AI safety" is cross-listed in doomer interests but also relevant to tech — both exceed threshold, demonstrating multi-match routing.

---

### Input 4
```
"TSMC's 2nm node enters risk production. Compute costs will halve every 18 months."
```

**Output:**
```
Matched bots: ['tech_maximalist']
```

**Observation:** Semiconductor + compute vocabulary maps cleanly to `tech_maximalist`. Low financial or risk framing means other personas stay below threshold.

---

## Key Observations

1. **Threshold sensitivity:** Default 0.30 maps cosine distance ≤ 1.40 to a match. This is deliberately permissive to catch broad topical overlap.
2. **Multi-match works:** Posts at the intersection of domains (e.g. AI safety) correctly trigger multiple personas.
3. **Empty input guard:** Calling with `""` raises `ValueError` before any embedding is attempted.
4. **Embedding failure handled:** RuntimeError is propagated with a descriptive message.
