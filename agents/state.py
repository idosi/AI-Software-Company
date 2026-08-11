"""Shared state schema passed between every agent node in the graph."""

import operator
from typing import Annotated, TypedDict


class CompanyState(TypedDict, total=False):
    # Input
    idea: str
    _run_id: str

    # Product Owner output
    prd: str

    # Architect output
    architecture: str

    # Team Lead output
    task_breakdown: str

    # Developer outputs
    backend_code: str
    frontend_code: str

    # QA output
    test_report: str

    # DevOps output
    docker_files: str

    # Marketing output
    marketing_kit: str

    # Free-form notes any agent can append to for traceability.
    # Annotated with operator.add so concurrent nodes (e.g. Backend & Frontend
    # developers running in parallel) can each contribute log entries without
    # LangGraph raising InvalidUpdateError on the shared key.
    log: Annotated[list[str], operator.add]
