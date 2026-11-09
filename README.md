# AI Software Company

A multi-agent system built on [LangGraph](https://langchain-ai.github.io/langgraph/) that simulates a small software company.
Give it a one-line app idea and a team of Claude-powered agents (Product Owner, Architect, Team Lead, Backend and Frontend Developers, QA, DevOps and Marketing) turns it into a PRD, an architecture, a task breakdown, code, tests, Docker/CI files and a marketing kit.

A second layer, defined in `CLAUDE.md`, lets the same roles work **inside a real GitHub repo**: they open issues, implement them on feature branches and open pull requests. The agents run autonomously up to a ready-for-review PR. **A human always approves and merges.**

## How it works

### 1. The generation pipeline (`main.py`)

```
                                          ┌─> Backend Developer ─┐
Idea ─> Product Owner ─> Architect ─> Team Lead                  ├─> Tester ─> DevOps ─> Marketing ─> Done
                                          └─> Frontend Developer ┘
```

| Agent | Input | Output |
|---|---|---|
| Product Owner | Raw idea | PRD (summary, users, MVP features, NFRs, out of scope) |
| Architect | PRD | Architecture doc (components, stack, data model, API contract, backend/frontend split) |
| Team Lead | Architecture | Prioritized task checklist with dependencies |
| Backend Developer | Architecture | Runnable backend code, one fenced block per file |
| Frontend Developer | Architecture | Runnable frontend code (React by default) |
| QA | Backend + frontend code | Unit/integration tests and a coverage-gap report |
| DevOps | Code + architecture | Dockerfiles, `docker-compose.yml`, GitHub Actions CI |
| Marketing | PRD | Pitch, positioning, social posts, landing page copy |

Design notes:

- The two developers run **in parallel** (fan-out) and the tester waits for both (fan-in).
- All agents share one typed state (`agents/state.py`). The `log` field uses `operator.add` so parallel nodes can append without conflicts.
- Every node **writes its artifact to disk immediately**, so partial results survive if a later node fails.
- One place builds the LLM client (`agents/llm.py`), so changing the model is a one-line change.

### 2. The GitHub workflow (`CLAUDE.md`)

The same roles run as trigger-based loops in [Claude Code](https://claude.com/claude-code). Each trigger does exactly one unit of work and then stops, which keeps context small and token cost low.

| Trigger | What happens |
|---|---|
| `run-architect` | Architect & PO write the PRD |
| `run-tl-breakdown` | Team Lead turns the PRD into labeled GitHub Issues on the project board |
| `run-tl-ready` | Team Lead moves unblocked issues from *Backlog* to *Ready for Dev* |
| `run-backend` / `run-frontend` / `run-devops` | Pick one issue, branch, implement, test, open a PR, move it to *In Review* |
| `run-tester` | Writes missing tests and runs the suite on every open PR |
| `run-reviewer` | Reviews one PR (security, quality, tests) and approves or requests changes |

Guardrails: one issue per run, a hard cap on files read, and **no agent ever merges a PR or moves an issue to Done**.

> `CLAUDE.md` always describes the project the company is **currently building** (right now: ExpiryGuard, with its own stack and design rules). Each target project gets its own version of the file. `CLAUDE.md_sportConnectApp.md` is the one used for the previous project, SportConnect.

## Project structure

```
.
├── main.py                  # Builds and runs the LangGraph StateGraph
├── langgraph.json           # Registers the graph for LangGraph Studio
├── agents/
│   ├── state.py             # Shared CompanyState schema
│   ├── llm.py               # Single ChatAnthropic client factory
│   ├── po_agent.py
│   ├── architect_agent.py
│   ├── team_lead_agent.py
│   ├── backend_developer_agent.py
│   ├── frontend_developer_agent.py
│   ├── qa_agent.py
│   ├── devops_agent.py
│   └── marketing_agent.py
├── outputs/<project>/       # Generated artifacts (prd/, code/, docker/, marketing/)
├── CLAUDE.md                # Claude Code loop definitions
├── requirements.txt
└── .env.example
```

## Getting started

**Requirements:** Python 3.10+ and an [Anthropic API key](https://console.anthropic.com/).

```bash
git clone https://github.com/idosi/ai-software-company.git
cd ai-software-company

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # then fill in your values
```

`.env`:

```
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=                  # optional, overrides the default model in agents/llm.py
```

### Run from the terminal

```bash
python main.py
# Describe your app idea: a platform for organizing local sports events
```

Results land in `outputs/`:

```
outputs/
├── prd/          prd_<run_id>.md, architecture_<run_id>.md, task_breakdown_<run_id>.md
├── code/         backend_<run_id>.md, frontend_<run_id>.md, tests_<run_id>.md
├── docker/       docker_<run_id>.md
└── marketing/    marketing_<run_id>.md
```

### Run in LangGraph Studio

```bash
langgraph dev
```

The graph is registered as `ai_software_company` in `langgraph.json`, so you can inspect each node, the state between nodes and the parallel branches visually.

## Example

`outputs/sportConnectApp/` holds a full run for **SportConnect**, a sports event platform: PRD, architecture, task breakdown, backend, frontend, tests, Docker files and marketing kit.

## Tech stack

Python · LangGraph · LangChain · Anthropic Claude (`langchain-anthropic`) · Pydantic · python-dotenv

## Limitations

- Generated code is delivered as Markdown documents, not written directly into a project tree. The GitHub workflow is what produces real commits and PRs.
- Output quality depends on the idea's clarity. Treat results as a strong first draft that needs human review.
- Agents do not execute the code they write inside the pipeline. Verification happens in the GitHub workflow through the Tester and Reviewer loops.

## Author

Built by [Ido Silberstein](https://github.com/idosi).
