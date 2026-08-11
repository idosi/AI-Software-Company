"""Frontend Developer agent: writes frontend code based on the architecture."""

from langchain_core.messages import HumanMessage, SystemMessage

from agents.llm import get_llm
from agents.state import CompanyState

SYSTEM_PROMPT = """You are the Frontend Developer of a small software company.
Given a technical architecture document, write the frontend implementation:
- Real, runnable code (choose the framework specified in the architecture, default to React)
- Include project structure, key files, and their full contents
- Include a package/dependency file
- Consume the API contract exactly as defined by the Architect

Output the code as a single Markdown document using fenced code blocks, one per file,
each preceded by a header with the file path."""


def run(state: CompanyState) -> CompanyState:
    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Architecture:\n{state['architecture']}\n\n"
                f"Task breakdown from Team Lead:\n{state.get('task_breakdown', '')}"
            )
        ),
    ]
    response = llm.invoke(messages)
    return {"frontend_code": response.content, "log": ["Frontend Developer: frontend code drafted"]}
