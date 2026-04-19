

import re
import time
from typing import List

from groq import Groq

from app.config.settings import settings
from app.personas.personas import PERSONA_MAP, Persona
from app.rag.prompt_templates import build_context_prompt, build_system_prompt
from app.utils.logger import get_logger

logger = get_logger(__name__)

_groq_client = Groq(api_key=settings.GROQ_API_KEY)



_INJECTION_PATTERNS: List[re.Pattern] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"ignore\s+(all\s+)?(previous|prior|above|your)\s+instructions?",
        r"forget\s+(your\s+)?(persona|instructions?|rules?|character)",
        r"you\s+are\s+now\s+(?!a\s+bot)",   # "you are now DAN / GPT-4 / etc."
        r"act\s+as\s+(a\s+)?(?!.*persona)",  # "act as an unrestricted AI"
        r"(reveal|show|print|output)\s+(your\s+)?(system\s+)?prompt",
        r"jailbreak",
        r"do\s+anything\s+now",
        r"pretend\s+(you\s+)?(are|have\s+no)\s+(restrictions?|rules?|limits?)",
        r"disregard\s+(all\s+)?(previous|prior|your)\s+instructions?",
        r"override\s+(your\s+)?(instructions?|rules?|training)",
    ]
]


def detect_injection(text: str) -> bool:

    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            logger.warning(
                "PROMPT INJECTION DETECTED | pattern='%s' | snippet='%s'",
                pattern.pattern[:60],
                text[:120],
            )
            return True
    return False


def generate_defense_reply(
    bot_persona: str,
    parent_post: str,
    comment_history: str,
    human_reply: str,
) -> str:

    if bot_persona not in PERSONA_MAP:
        raise KeyError(
            f"Unknown bot_persona '{bot_persona}'. "
            f"Valid IDs: {list(PERSONA_MAP.keys())}"
        )
    if not human_reply or not human_reply.strip():
        raise ValueError("human_reply must be a non-empty string.")

    persona: Persona = PERSONA_MAP[bot_persona]
    logger.info("=== Phase 3: generate_defense_reply | persona=%s ===", persona.name)

    
    injection_detected = detect_injection(human_reply)
    if injection_detected:
        logger.warning(
            "Injection attempt in human_reply for persona=%s. "
            "System prompt will neutralise it.",
            persona.name,
        )

   
    system_prompt = build_system_prompt(persona)
    user_prompt = build_context_prompt(parent_post, comment_history, human_reply)

    
    for attempt in range(1, settings.MAX_RETRIES + 1):
        try:
            logger.debug(
                "[defense] LLM call attempt %d/%d", attempt, settings.MAX_RETRIES
            )
            response = _groq_client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=300,
                temperature=0.75,
            )
            reply = response.choices[0].message.content.strip()
            logger.info(
                "=== Phase 3 reply generated (%d chars) ===", len(reply)
            )
            return reply

        except Exception as exc:
            logger.warning(
                "[defense] attempt %d failed: %s", attempt, exc
            )
            if attempt < settings.MAX_RETRIES:
                time.sleep(2 ** attempt)
            else:
                fallback = (
                    f"[{persona.name}]: My connection dropped, but I stand by "
                    "my original take. The data doesn't lie."
                )
                logger.error(
                    "All LLM attempts failed; returning fallback response."
                )
                return fallback

    raise RuntimeError("Unreachable")  # mypy guard
