"""Team Lead agent: breaks the architecture into dev tasks for the developers."""

from langchain_core.messages import HumanMessage, SystemMessage

from agents.llm import get_llm
from agents.state import CompanyState

SYSTEM_PROMPT = """You are the Team Lead of a small software company.
Given a technical architecture document, break it down into a concrete task list
for the Backend Developer and Frontend Developer, with priorities and dependencies
between tasks called out explicitly. Output in Markdown as a checklist."""


def run(state: CompanyState) -> CompanyState:
    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Architecture:\n{state['architecture']}"),
    ]
    response = llm.invoke(messages)
    return {"task_breakdown": response.content, "log": ["Team Lead: task breakdown drafted"]}
