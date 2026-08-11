"""Product Owner agent: turns a raw idea into a PRD."""

from langchain_core.messages import HumanMessage, SystemMessage

from agents.llm import get_llm
from agents.state import CompanyState

SYSTEM_PROMPT = """You are the Product Owner of a small software company.
Given a raw product idea, write a clear, concise Product Requirements Document (PRD) with:
1. Product summary
2. Target users
3. Core features (MVP scope only)
4. Non-functional requirements (performance, scalability, security)
5. Out-of-scope items

Be concrete and avoid filler. Output in Markdown."""


def run(state: CompanyState) -> CompanyState:
    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Product idea:\n{state['idea']}"),
    ]
    response = llm.invoke(messages)
    return {"prd": response.content, "log": ["PO: PRD drafted"]}
