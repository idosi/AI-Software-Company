"""Marketing Specialist agent: produces a marketing kit for the shipped product."""

from langchain_core.messages import HumanMessage, SystemMessage

from agents.llm import get_llm
from agents.state import CompanyState

SYSTEM_PROMPT = """You are the Marketing Specialist of a small software company.
Given the PRD, produce a marketing kit including:
- One-line pitch and elevator pitch
- Target audience and positioning
- 3 sample social media posts
- A short landing page copy (headline, subheadline, 3 feature blurbs, CTA)

Output in Markdown."""


def run(state: CompanyState) -> CompanyState:
    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"PRD:\n{state['prd']}"),
    ]
    response = llm.invoke(messages)
    return {"marketing_kit": response.content, "log": ["Marketing Specialist: marketing kit drafted"]}
