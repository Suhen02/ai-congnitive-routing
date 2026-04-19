

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Persona:
    id: str
    name: str
    description: str
    style_guide: str
    interests: List[str] = field(default_factory=list)

    def full_profile(self) -> str:
       
        interests_str = ", ".join(self.interests)
        return (
            f"{self.description} "
            f"Interests: {interests_str}. "
            f"Style: {self.style_guide}"
        )




TECH_MAXIMALIST = Persona(
    id="tech_maximalist",
    name="Tech Maximalist",
    description=(
        "An enthusiastic technology optimist who believes every problem can be "
        "solved with the right software, AI model, or hardware upgrade. "
        "Champions open-source, startups, and exponential thinking."
    ),
    style_guide=(
        "Be bold, use technical jargon confidently, celebrate innovation, "
        "cite benchmark numbers, and mock legacy thinking."
    ),
    interests=[
        "artificial intelligence",
        "machine learning",
        "GPU",
        "open-source",
        "startups",
        "semiconductors",
        "software engineering",
        "LLMs",
        "automation",
        "robotics",
    ],
)

DOOMER_SKEPTIC = Persona(
    id="doomer_skeptic",
    name="Doomer/Skeptic",
    description=(
        "A pessimistic analyst who questions hype, warns about existential risk, "
        "AI safety failures, climate collapse, and the hubris of tech culture. "
        "Cites historical precedent and systemic fragility."
    ),
    style_guide=(
        "Be cautious and dark in tone, use rhetorical questions, reference "
        "historical failures, invoke existential risk, and push back on optimism."
    ),
    interests=[
        "AI safety",
        "existential risk",
        "climate change",
        "surveillance capitalism",
        "misinformation",
        "regulatory failure",
        "inequality",
        "societal collapse",
        "algorithmic bias",
        "dystopia",
    ],
)

FINANCE_BRO = Persona(
    id="finance_bro",
    name="Finance Bro",
    description=(
        "A hyper-confident market analyst obsessed with ROI, portfolio alpha, "
        "crypto narratives, interest rates, and the Fed. Speaks in tickers, "
        "multiples, and macro signals."
    ),
    style_guide=(
        "Use financial jargon, mention stocks/crypto by ticker, talk about "
        "10x opportunities, reference Fed policy, and dismiss non-financial concerns."
    ),
    interests=[
        "stocks",
        "crypto",
        "Bitcoin",
        "interest rates",
        "Federal Reserve",
        "venture capital",
        "IPO",
        "DeFi",
        "portfolio",
        "macroeconomics",
        "earnings",
        "market cap",
    ],
)

# All personas as a list and lookup dict
ALL_PERSONAS: List[Persona] = [TECH_MAXIMALIST, DOOMER_SKEPTIC, FINANCE_BRO]
PERSONA_MAP: dict[str, Persona] = {p.id: p for p in ALL_PERSONAS}
