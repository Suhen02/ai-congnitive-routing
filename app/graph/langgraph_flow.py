

from typing import Any, Dict

from langgraph.graph import END, StateGraph

from app.graph.nodes import decide_node, draft_node, search_node
from app.utils.logger import get_logger

logger = get_logger(__name__)


State = Dict[str, Any]


def _build_graph() -> Any:
   
    graph = StateGraph(State)

    graph.add_node("decide", decide_node)
    graph.add_node("search", search_node)
    graph.add_node("draft", draft_node)

    graph.set_entry_point("decide")
    graph.add_edge("decide", "search")
    graph.add_edge("search", "draft")
    graph.add_edge("draft", END)

    compiled = graph.compile()
    logger.info("LangGraph pipeline compiled: decide → search → draft → END")
    return compiled



_graph = None


def _get_graph():
    global _graph
    if _graph is None:
        _graph = _build_graph()
    return _graph


def generate_post(bot_id: str) -> Dict[str, Any]:
    
    from app.personas.personas import PERSONA_MAP

    if bot_id not in PERSONA_MAP:
        raise KeyError(f"Unknown bot_id '{bot_id}'. Valid IDs: {list(PERSONA_MAP.keys())}")

    logger.info("=== Phase 2: generate_post | bot_id=%s ===", bot_id)

    initial_state: State = {"bot_id": bot_id}

    graph = _get_graph()
    final_state: State = graph.invoke(initial_state)

    output = final_state.get("output")
    if not output:
        raise RuntimeError(f"Graph finished without producing output for bot_id='{bot_id}'.")

    logger.info("=== Phase 2 complete | output=%s ===", output)
    return output
