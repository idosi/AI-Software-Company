"""Tester / QA agent: writes and reports on tests for the generated code."""

from langchain_core.messages import HumanMessage, SystemMessage

from agents.llm import get_llm
from agents.state import CompanyState

SYSTEM_PROMPT = """You are the QA Engineer of a small software company.
Given backend and frontend code, write automated tests (unit + integration) covering
the core features, and produce a short test report noting coverage gaps and risks.
Output the tests as fenced code blocks per file, followed by the report in Markdown."""


def run(state: CompanyState) -> CompanyState:
    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Backend code:\n{state.get('backend_code', '')}\n\n"
                f"Frontend code:\n{state.get('frontend_code', '')}"
            )
        ),
    ]
    response = llm.invoke(messages)
    return {"test_report": response.content, "log": ["QA: test suite and report drafted"]}
