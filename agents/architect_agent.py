"""Architect agent: turns a PRD into a technical architecture and dev plan."""

from langchain_core.messages import HumanMessage, SystemMessage

from agents.llm import get_llm
from agents.state import CompanyState

SYSTEM_PROMPT = """You are the Software Architect of a small software company.
Given a Product Requirements Document (PRD), produce a technical architecture document with:
1. High-level system architecture (components + how they interact)
2. Tech stack choice with justification (backend, frontend, database, infra)
3. Data model / key entities
4. API contract (main endpoints, request/response shape)
5. Explicit split of responsibilities between the Backend Developer and Frontend Developer

Be concrete and avoid filler. Output in Markdown."""


def run(state: CompanyState) -> CompanyState:
    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"PRD:\n{state['prd']}"),
    ]
    response = llm.invoke(messages)
    return {"architecture": response.content, "log": ["Architect: architecture drafted"]}
