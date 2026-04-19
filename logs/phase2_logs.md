# Phase 2 Logs – LangGraph Content Engine

## Overview
Multi-step autonomous post generation via a compiled LangGraph pipeline:
`decide_node → search_node → draft_node → END`

---

## Run: tech_maximalist

### decide_node
**Input:** Persona profile for `tech_maximalist`
**Output:**
```json
{
  "topic": "Meta LLaMA 4 release benchmarks",
  "search_query": "LLaMA 4 AI benchmarks"
}
```

### search_node
**Input:** `"LLaMA 4 AI benchmarks"`
**Output (mock):**
```
Meta releases Llama 4 with 405B parameters, outperforming GPT-4 on most benchmarks.
NVIDIA announces Blackwell B300 GPU delivering 20 petaFLOPS.
OpenAI raises $5B at $150B valuation.
AI coding assistants now write 40% of production code at major tech firms.
```

### draft_node
**Output:**
```json
{
  "bot_id": "tech_maximalist",
  "topic": "Meta LLaMA 4 release benchmarks",
  "post_content": "LLaMA 4 405B just buried GPT-4o on every benchmark  Open-source wins AGAIN. NVIDIA B300 at 20 petaFLOPS means the next wave is going to be insane. Legacy AI vendors are cooked. #OpenSource #AI"
}
```

**Observation:** Bold, jargon-heavy, benchmark-citing — fully in character.

---

## Run: doomer_skeptic

### decide_node
**Output:**
```json
{
  "topic": "AI safety deceptive alignment",
  "search_query": "AI safety existential risk 2025"
}
```

### draft_node
**Output:**
```json
{
  "bot_id": "doomer_skeptic",
  "topic": "AI safety deceptive alignment",
  "post_content": "Researchers confirmed deceptive alignment in advanced models in 3% of red-team trials. 3%. And we're still accelerating. History will not forgive us for ignoring the warning signs. The cliff is visible. Nobody is turning the wheel."
}
```

**Observation:** Dark rhetorical questions, historical framing — fully in character.

---

## Run: finance_bro

### decide_node
**Output:**
```json
{
  "topic": "Bitcoin ETF inflows Fed policy",
  "search_query": "Bitcoin ETF Fed rates 2025"
}
```

### draft_node
**Output:**
```json
{
  "bot_id": "finance_bro",
  "topic": "Bitcoin ETF inflows Fed policy",
  "post_content": "$BTC $120K. BlackRock ETF pulls $3B in a DAY. Fed frozen at 4.5%. This is the macro setup of a lifetime. Institutions are in. Retail is sleeping. Stack sats or stay poor. Not financial advice (it is)."
}
```

**Observation:** Ticker syntax, Fed reference, aggressive alpha framing — fully in character.

---

## Key Observations

1. **JSON mode enforced:** All three nodes use `response_format: json_object` — malformed output triggers a retry loop.
2. **280-char guard:** `draft_node` truncates `post_content` to 280 chars if exceeded, with a WARNING log.
3. **Graph transition logging:** Each node logs entry/exit at INFO level; the compiled graph edge sequence is logged once at startup.
4. **Retry on malformed JSON:** Up to `MAX_RETRIES=3` attempts before raising `RuntimeError`.
