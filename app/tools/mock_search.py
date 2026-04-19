

import re
from typing import Dict

from app.utils.logger import get_logger

logger = get_logger(__name__)


_RESULTS_DB: Dict[str, str] = {
  
    "ai|llm|gpt|model|language model|neural|deep learning|machine learning": (
        "Meta releases Llama 4 with 405B parameters, outperforming GPT-4 on "
        "most benchmarks. NVIDIA announces Blackwell B300 GPU delivering "
        "20 petaFLOPS. OpenAI raises $5B at $150B valuation. "
        "AI coding assistants now write 40% of production code at major tech firms."
    ),
    # Crypto / Finance
    "bitcoin|crypto|ethereum|defi|blockchain|web3|nft": (
        "Bitcoin breaks $120K as BlackRock's spot ETF records $3B single-day "
        "inflows. Ethereum layer-2 TVL surpasses $80B. SEC approves Ether "
        "staking ETFs. DeFi protocol Aave crosses $20B in active loans."
    ),
    # Stocks / Market
    "stock|market|nasdaq|sp500|fed|rates|inflation|earnings|ipo": (
        "S&P 500 hits all-time high of 6,200. Fed holds rates at 4.5% citing "
        "resilient labour market. Apple earnings beat by 12%. "
        "Stripe files confidentially for IPO at $80B valuation."
    ),
    # Climate / Risk
    "climate|carbon|environment|risk|collapse|existential|safety": (
        "IPCC issues red alert: 2025 on track to be hottest year on record. "
        "Permafrost methane release accelerates beyond models. "
        "AI safety researchers warn o3-level models exhibit deceptive alignment "
        "in 3% of red-team trials."
    ),
    # Robotics / Hardware
    "robot|hardware|chip|semiconductor|quantum|compute": (
        "Tesla Optimus Gen-3 walks at 6 km/h and folds laundry unassisted. "
        "TSMC 2nm node enters risk production. "
        "Google claims quantum supremacy on 100-qubit processor."
    ),
}

_DEFAULT_RESULT = (
    "Breaking: Global tech investment reaches $1.2T in 2025, up 34% YoY. "
    "Regulatory crackdowns on AI expected in EU. "
    "Emerging markets drive 60% of new internet user growth."
)


def mock_searxng_search(query: str) -> str:
   
    if not query or not query.strip():
        logger.warning("mock_searxng_search called with empty query.")
        return _DEFAULT_RESULT

    query_lower = query.lower()
    logger.info("Mock search | query='%s'", query)

    for pattern, result in _RESULTS_DB.items():
        keywords = pattern.split("|")
        if any(kw in query_lower for kw in keywords):
            logger.debug("Search matched pattern '%s'", pattern[:40])
            return result

    logger.debug("No pattern matched; returning default search result.")
    return _DEFAULT_RESULT
