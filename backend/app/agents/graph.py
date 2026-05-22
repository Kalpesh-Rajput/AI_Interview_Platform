from langgraph.graph import END, StateGraph

try:
    from langsmith import traceable
except ImportError:
    def traceable(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

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


@traceable(name="Interview Pipeline", run_type="chain")
async def run_interview_pipeline(jd_text: str, resume_text: str) -> dict:
    from app.core.config import token_tracker
    token_tracker.set({
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "input_cost": 0.0,
        "output_cost": 0.0,
        "total_cost": 0.0
    })

    initial: InterviewState = {
        "jd_text": jd_text,
        "resume_text": resume_text,
        "retry_count": 0,
        "supervisor_feedback": "",
    }
    result = await interview_graph.ainvoke(initial)
    supervisor = result.get("supervisor_result")

    tracker = token_tracker.get()
    usage_metadata = None
    if tracker:
        prompt_t = tracker.get("prompt_tokens", 0)
        completion_t = tracker.get("completion_tokens", 0)
        total_t = prompt_t + completion_t
        usage_metadata = {
            "input_tokens": prompt_t,
            "output_tokens": completion_t,
            "total_tokens": total_t,
            "prompt_tokens": prompt_t,
            "completion_tokens": completion_t,
            "input_cost": tracker.get("input_cost", 0.0),
            "output_cost": tracker.get("output_cost", 0.0),
            "total_cost": tracker.get("total_cost", 0.0)
        }

        try:
            from langsmith import get_current_run_tree
            run_tree = get_current_run_tree()
            if run_tree:
                try:
                    if run_tree.outputs is None:
                        run_tree.outputs = {}
                    run_tree.outputs["usage_metadata"] = usage_metadata
                    run_tree.outputs["response_metadata"] = {
                        "token_usage": {
                            "prompt_tokens": prompt_t,
                            "completion_tokens": completion_t,
                            "total_tokens": total_t
                        }
                    }
                except Exception:
                    pass
                
                try:
                    if run_tree.extra is None:
                        run_tree.extra = {}
                    run_tree.extra["token_usage"] = {
                        "prompt_tokens": prompt_t,
                        "completion_tokens": completion_t,
                        "total_tokens": total_t
                    }
                    run_tree.extra["usage_metadata"] = usage_metadata
                    
                    if run_tree.metadata is not None:
                        run_tree.metadata["usage_metadata"] = usage_metadata
                        run_tree.metadata["token_usage"] = {
                            "prompt_tokens": prompt_t,
                            "completion_tokens": completion_t,
                            "total_tokens": total_t
                        }
                except Exception:
                    pass
        except Exception:
            pass

    ret = {
        "questions": result.get("questions", []),
        "context": result.get("context"),
        "retries": result.get("retry_count", 0),
        "quality_score": supervisor.quality_score if supervisor else 0.0,
    }
    if usage_metadata:
        ret["usage_metadata"] = usage_metadata
    return ret
