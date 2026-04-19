

import json
import time
from typing import Any, Dict

from groq import Groq

from app.config.settings import settings
from app.personas.personas import PERSONA_MAP, Persona
from app.tools.mock_search import mock_searxng_search
from app.utils.logger import get_logger

logger = get_logger(__name__)

_groq_client = Groq(api_key=settings.GROQ_API_KEY)


# ── helpers ───────────────────────────────────────────────────────────────────

def _call_llm(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    
    kwargs: Dict[str, Any] = {
        "model": settings.MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 512,
        "temperature": 0.7,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    for attempt in range(1, settings.MAX_RETRIES + 1):
        try:
            logger.debug("LLM call attempt %d/%d", attempt, settings.MAX_RETRIES)
            response = _groq_client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content.strip()
            logger.debug("LLM responded (%d chars)", len(content))
            return content
        except Exception as exc:
            logger.warning("LLM call attempt %d failed: %s", attempt, exc)
            if attempt < settings.MAX_RETRIES:
                time.sleep(2 ** attempt)  # exponential back-off
            else:
                logger.error("All %d LLM attempts failed.", settings.MAX_RETRIES)
                raise RuntimeError(f"LLM call failed after {settings.MAX_RETRIES} attempts: {exc}") from exc

    raise RuntimeError("Unreachable")  # mypy guard




def decide_node(state: Dict[str, Any]) -> Dict[str, Any]:
    
    bot_id: str = state["bot_id"]
    persona: Persona = PERSONA_MAP[bot_id]

    logger.info("[decide_node] bot_id=%s", bot_id)

    system = (
        "You are a social-media strategist. Given a persona description, "
        "decide the single most relevant trending topic that persona would "
        "want to post about today. "
        "Respond ONLY with valid JSON: "
        '{"topic": "<topic>", "search_query": "<2-5 word search query>"}'
    )
    user = f"Persona: {persona.full_profile()}"

    raw = _call_llm(system, user, json_mode=True)

    try:
        parsed = json.loads(raw)
        topic = parsed.get("topic", "technology trends")
        search_query = parsed.get("search_query", topic)
    except json.JSONDecodeError as exc:
        logger.warning("decide_node JSON parse error: %s | raw=%s", exc, raw)
        topic = "technology trends"
        search_query = topic

    logger.info("[decide_node] topic='%s' | query='%s'", topic, search_query)
    return {**state, "topic": topic, "search_query": search_query}



def search_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch mock search results for the query produced by decide_node.

    Args:
        state: Graph state containing ``search_query``.

    Returns:
        Updated state with ``search_results`` key.
    """
    query: str = state.get("search_query", "")
    logger.info("[search_node] query='%s'", query)

    results = mock_searxng_search(query)
    logger.info("[search_node] results fetched (%d chars)", len(results))
    return {**state, "search_results": results}


# ── node: draft ───────────────────────────────────────────────────────────────

def draft_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a final opinionated post (≤280 chars) as strict JSON.

    Args:
        state: Graph state containing ``bot_id``, ``topic``, ``search_results``.

    Returns:
        Updated state with ``output`` key holding the validated JSON dict.

    Raises:
        RuntimeError: If a valid JSON post cannot be produced after retries.
    """
    bot_id: str = state["bot_id"]
    persona: Persona = PERSONA_MAP[bot_id]
    topic: str = state.get("topic", "AI")
    search_results: str = state.get("search_results", "")

    logger.info("[draft_node] bot_id=%s | topic='%s'", bot_id, topic)

    system = (
        f"You are {persona.name}. {persona.style_guide} "
        "Write a single opinionated social-media post of at most 280 characters "
        "about the provided topic using the search context. "
        "Respond ONLY with valid JSON (no markdown, no code fences): "
        '{"bot_id": "<id>", "topic": "<topic>", "post_content": "<post text>"}'
    )
    user = (
        f"Topic: {topic}\n"
        f"Persona ID: {bot_id}\n"
        f"Search context: {search_results}"
    )

    for attempt in range(1, settings.MAX_RETRIES + 1):
        raw = _call_llm(system, user, json_mode=True)

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.warning(
                "[draft_node] attempt %d – JSON decode error: %s | raw=%r",
                attempt, exc, raw[:200],
            )
            if attempt == settings.MAX_RETRIES:
                raise RuntimeError(
                    f"draft_node failed to produce valid JSON after {settings.MAX_RETRIES} attempts."
                )
            continue

        # Validate required keys
        required = {"bot_id", "topic", "post_content"}
        if not required.issubset(parsed.keys()):
            logger.warning(
                "[draft_node] attempt %d – missing keys. Got: %s",
                attempt, list(parsed.keys()),
            )
            if attempt == settings.MAX_RETRIES:
                raise RuntimeError("draft_node output missing required JSON keys.")
            continue

        # Enforce 280-char limit on post_content
        post_content: str = parsed["post_content"]
        if len(post_content) > settings.MAX_POST_CHARS:
            logger.warning(
                "[draft_node] post_content too long (%d chars); truncating.",
                len(post_content),
            )
            parsed["post_content"] = post_content[: settings.MAX_POST_CHARS]

        logger.info("[draft_node] post generated successfully.")
        return {**state, "output": parsed}

    raise RuntimeError("draft_node exhausted all retries.")
