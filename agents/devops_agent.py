"""DevOps agent: produces Dockerfiles, compose files, and CI config."""

from langchain_core.messages import HumanMessage, SystemMessage

from agents.llm import get_llm
from agents.state import CompanyState

SYSTEM_PROMPT = """You are the DevOps Engineer of a small software company.
Given backend and frontend code and the architecture doc, produce:
- A Dockerfile for the backend
- A Dockerfile for the frontend
- A docker-compose.yml wiring them together (plus database if needed)
- A minimal CI pipeline config (GitHub Actions) that builds and runs tests

Output each as a fenced code block preceded by its file path."""


def run(state: CompanyState) -> CompanyState:
    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Architecture:\n{state['architecture']}\n\n"
                f"Backend code:\n{state.get('backend_code', '')}\n\n"
                f"Frontend code:\n{state.get('frontend_code', '')}"
            )
        ),
    ]
    response = llm.invoke(messages)
    return {"docker_files": response.content, "log": ["DevOps: docker & CI files drafted"]}
