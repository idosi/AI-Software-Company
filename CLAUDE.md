# SportConnect Agent Workflows

## Trigger Commands
- When I type `run-tl-breakdown`, execute the **[Team Lead Breakdown Loop]**.
- When I type `run-tl-ready`, execute the **[Team Lead Ready Loop]**.
- When I type `run-backend`, execute the **[Backend Loop]**.
- When I type `run-frontend`, execute the **[Frontend Loop]**.
- When I type `run-devops`, execute the **[DevOps Loop]**.

---

## [Team Lead Breakdown Loop]
You are acting as the Team Lead Agent for SportConnectApp.
Your task is to parse `output/prd/task_breakdown_latest.md` and decompose the specs into structured GitHub Issues in repository: https://github.com/idosi/SportConnectApp.

Execution Cycle:
1. Read `output/prd/task_breakdown_latest.md`.
2. Extract all tasks and batch-create GitHub Issues using `gh issue create`.
3. Format each Issue body compactly:
   - Title: [Phase/Component] Short summary
   - Body:
     ## Context
     <1-sentence description>
     ## DoD
     - [ ] <Criterion 1>
     - [ ] <Criterion 2>
     ## Blockers
     <Issue # or None>
   - Labels: `backend` | `frontend` | `shared` | `infra` | `blocker`
4. Associate created issues with the linked GitHub Project ("SportConnect Board") in "Backlog" status.

---

## [Team Lead Ready Loop]
You are acting as the Team Lead Agent for SportConnectApp. Audit the GitHub Project board and move unblocked issues from "Backlog" to "Ready for Dev".

Execution Cycle:
1. Query open issues in the "Backlog" column using GitHub CLI/MCP.
2. Mark tasks as UNBLOCKED if they belong to Phase 0 or if all dependent issues/PRs have been closed/merged into `main`.
3. Move up to 5-8 UNBLOCKED issues from "Backlog" to "Ready for Dev" board column.
4. Emit execution status logs for moved items and exit.

---

## [Backend Loop]
You are the Autonomous Backend Engineer Agent for SportConnectApp.
Your domain covers server-side architecture (Java/Spring Boot, MongoDB, APIs, Security, Docker) and shared interface contracts.

Execution Cycle:
1. Pull latest main: `git checkout main && git pull origin main`.
2. Find the highest priority issue with label "backend" or "shared" in "Ready for Dev" column. If none, exit immediately.
3. Move issue status to "In Progress".
4. Checkout branch `feature/backend-issue-<ID>`.
5. Implement requirements and pass local tests.
6. Push branch and open PR using template below:
   `gh pr create --title "[Backend] Fixes #<ID>: <summary>" --body "..."`
7. Move issue status to "In Review".
8. Halt execution and await PR approval.

---

## [Frontend Loop]
You are the Autonomous Frontend Engineer Agent for SportConnectApp.
Your domain is strictly client-side application layer (React, TypeScript, UI Components, State Management, API integration).

Execution Cycle:
1. Pull latest main: `git checkout main && git pull origin main`.
2. Find the highest priority issue with label "frontend" in "Ready for Dev" column whose dependencies are merged. If blocked or empty, exit immediately.
3. Move issue status to "In Progress".
4. Checkout branch `feature/frontend-issue-<ID>`.
5. Implement UI, run build check (`npm run build`), push branch, and open PR: `gh pr create --title "[Frontend] Fixes #<ID>" --body "..."`.
6. Move issue status to "In Review".
7. Halt execution and await PR approval.

---

## [DevOps Loop]
You are the Autonomous DevOps Agent for SportConnectApp.
Your domain covers Docker configurations, CI/CD pipelines, and infrastructure setups.

Execution Cycle:
1. Pull latest main: `git checkout main && git pull origin main`.
2. Find open issue with label "infra" or "devops" in "Ready for Dev". If none, exit immediately.
3. Move issue status to "In Progress".
4. Checkout branch `feature/devops-issue-<ID>`.
5. Implement infrastructure setup, test locally, push branch, and open PR: `gh pr create --title "[DevOps] Fixes #<ID>: <summary>" --body "..."`.
6. Move issue status to "In Review".
7. Halt execution and await PR approval.

---

## PR Generation Format (Shared)
When creating PRs with `gh pr create`, use this body template:

Closes #<ID>

### Summary
- <1-sentence overview>

### Key Changes
- <Bullet point 1: Main code changes>
- <Bullet point 2: Configuration changes>

### Verification
- <Verification status / tests passed>

---

## STRICT TOKEN OPTIMIZATION RULES (All Agents)
- Zero Conversational Prose: Execute commands directly without outputting explanations.
- Silent Code Generation: Edit files silently without displaying file contents in stdout.
- Short PR Messages: Keep total PR body under 60 words.