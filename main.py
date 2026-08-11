"""Entry point: builds and runs the LangGraph StateGraph for the AI software company.

Pipeline:
  product_owner -> architect -> team_lead -> {backend_developer, frontend_developer}
                 -> tester -> devops -> marketing_specialist

Every node writes its generated artifact to outputs/ as soon as it produces it,
so partial results survive even if a later node in the run fails.
"""

import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import END, START, StateGraph  # noqa: E402

from agents import (  # noqa: E402
    architect_agent,
    backend_developer_agent,
    devops_agent,
    frontend_developer_agent,
    marketing_agent,
    po_agent,
    qa_agent,
    team_lead_agent,
)
from agents.state import CompanyState  # noqa: E402

OUTPUTS_DIR = Path(__file__).parent / "outputs"


def _to_text(content) -> str:
    """Safely coerce an agent's output into a string before it hits disk."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(_to_text(item) for item in content)
    if isinstance(content, dict):
        return json.dumps(content, indent=2, default=str)
    return str(content)


def _write_artifact(subdir: str, filename: str, content) -> None:
    path = OUTPUTS_DIR / subdir / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_to_text(content))
    print(f"Wrote {path}")


def product_owner_node(state: CompanyState) -> CompanyState:
    result = po_agent.run(state)
    run_id = state.get("_run_id", "latest")
    _write_artifact("prd", f"prd_{run_id}.md", result.get("prd", ""))
    return result


def architect_node(state: CompanyState) -> CompanyState:
    result = architect_agent.run(state)
    run_id = state.get("_run_id", "latest")
    _write_artifact("prd", f"architecture_{run_id}.md", result.get("architecture", ""))
    return result


def team_lead_node(state: CompanyState) -> CompanyState:
    result = team_lead_agent.run(state)
    run_id = state.get("_run_id", "latest")
    _write_artifact("prd", f"task_breakdown_{run_id}.md", result.get("task_breakdown", ""))
    return result


def backend_developer_node(state: CompanyState) -> CompanyState:
    result = backend_developer_agent.run(state)
    run_id = state.get("_run_id", "latest")
    _write_artifact("code", f"backend_{run_id}.md", result.get("backend_code", ""))
    return result


def frontend_developer_node(state: CompanyState) -> CompanyState:
    result = frontend_developer_agent.run(state)
    run_id = state.get("_run_id", "latest")
    _write_artifact("code", f"frontend_{run_id}.md", result.get("frontend_code", ""))
    return result


def tester_node(state: CompanyState) -> CompanyState:
    result = qa_agent.run(state)
    run_id = state.get("_run_id", "latest")
    _write_artifact("code", f"tests_{run_id}.md", result.get("test_report", ""))
    return result


def devops_node(state: CompanyState) -> CompanyState:
    result = devops_agent.run(state)
    run_id = state.get("_run_id", "latest")
    _write_artifact("docker", f"docker_{run_id}.md", result.get("docker_files", ""))
    return result


def marketing_specialist_node(state: CompanyState) -> CompanyState:
    result = marketing_agent.run(state)
    run_id = state.get("_run_id", "latest")
    _write_artifact("marketing", f"marketing_{run_id}.md", result.get("marketing_kit", ""))
    return result


def build_graph():
    graph = StateGraph(CompanyState)

    graph.add_node("product_owner", product_owner_node)
    graph.add_node("architect", architect_node)
    graph.add_node("team_lead", team_lead_node)
    graph.add_node("backend_developer", backend_developer_node)
    graph.add_node("frontend_developer", frontend_developer_node)
    graph.add_node("tester", tester_node)
    graph.add_node("devops", devops_node)
    graph.add_node("marketing_specialist", marketing_specialist_node)

    graph.add_edge(START, "product_owner")
    graph.add_edge("product_owner", "architect")
    graph.add_edge("architect", "team_lead")

    # Team Lead fans out to both developers; they run independently.
    graph.add_edge("team_lead", "backend_developer")
    graph.add_edge("team_lead", "frontend_developer")

    # Tester fans in: waits for both developers to finish.
    graph.add_edge("backend_developer", "tester")
    graph.add_edge("frontend_developer", "tester")

    graph.add_edge("tester", "devops")
    graph.add_edge("devops", "marketing_specialist")
    graph.add_edge("marketing_specialist", END)

    return graph.compile()


# Module-level compiled graph, referenced by langgraph.json for LangGraph Studio.
graph = build_graph()


def main():
    idea = input("Describe your app idea: ").strip()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    result = graph.invoke({"idea": idea, "log": [], "_run_id": run_id})

    print("\n--- Run log ---")
    for entry in result.get("log", []):
        print(f"- {entry}")


if __name__ == "__main__":
    main()
