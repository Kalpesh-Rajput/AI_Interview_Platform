from langgraph.graph import END, StateGraph

from app.agents.nodes.context import context_extraction_agent
from app.agents.nodes.explanation import explanation_agent
from app.agents.nodes.parsing import parsing_agent
from app.agents.nodes.questions import question_generation_agent
from app.agents.nodes.supervisor import should_regenerate, supervisor_agent
from app.agents.state import InterviewState


def build_interview_graph():
    graph = StateGraph(InterviewState)

    graph.add_node("parsing", parsing_agent)
    graph.add_node("context_extraction", context_extraction_agent)
    graph.add_node("question_generation", question_generation_agent)
    graph.add_node("explanation", explanation_agent)
    graph.add_node("supervisor", supervisor_agent)

    graph.set_entry_point("parsing")
    graph.add_edge("parsing", "context_extraction")
    graph.add_edge("context_extraction", "question_generation")
    graph.add_edge("question_generation", "explanation")
    graph.add_edge("explanation", "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        should_regenerate,
        {
            "regenerate": "question_generation",
            "end": END,
        },
    )

    return graph.compile()


interview_graph = build_interview_graph()


async def run_interview_pipeline(jd_text: str, resume_text: str) -> dict:
    initial: InterviewState = {
        "jd_text": jd_text,
        "resume_text": resume_text,
        "retry_count": 0,
        "supervisor_feedback": "",
    }
    result = await interview_graph.ainvoke(initial)
    supervisor = result.get("supervisor_result")
    return {
        "questions": result.get("questions", []),
        "context": result.get("context"),
        "retries": result.get("retry_count", 0),
        "quality_score": supervisor.quality_score if supervisor else 0.0,
    }
