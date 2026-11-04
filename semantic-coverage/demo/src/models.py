from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AssertRecord(BaseModel):
    """A single assertion-like statement with exact source location."""

    line_start: int
    line_end: int
    source: str
    kind: Literal["assert", "raises"] = "assert"


class TestRecord(BaseModel):
    """One test function extracted from the repository."""

    id: str
    file: str
    name: str
    qualname: str
    line_start: int
    line_end: int
    docstring: str = ""
    asserts: list[AssertRecord] = Field(default_factory=list)
    signals: list[str] = Field(default_factory=list)
    search_text: str = ""
    body_text: str = ""
    has_asserts: bool = False
    domain: str | None = None


class AC(BaseModel):
    id: str
    text_ru: str
    text_en: str
    weight: int = Field(ge=1, le=3)
    check: str
    keywords: list[str] = Field(min_length=1)
    excludes: list[str] = Field(default_factory=list)


class Requirement(BaseModel):
    id: str
    title: str
    weight: int = Field(ge=1, le=3)
    gherkin: str = ""
    acceptance_criteria: list[AC] = Field(min_length=1)

    @field_validator("acceptance_criteria")
    @classmethod
    def _unique_ac_ids(cls, v: list[AC]) -> list[AC]:
        ids = [a.id for a in v]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate acceptance criteria ids")
        return v


class RequirementsFile(BaseModel):
    schema_version: int
    language: str
    requirements: list[Requirement] = Field(min_length=1)


class Status(str, Enum):
    covered = "covered"
    partial = "partial"
    absent = "absent"


class Evidence(BaseModel):
    test_id: str
    file: str
    line_start: int
    line_end: int
    quote: str


class ACResult(BaseModel):
    ac_id: str
    status: Status
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[Evidence] = Field(default_factory=list)
    reasoning: str = ""


class RequirementResult(BaseModel):
    requirement_id: str
    acs: list[ACResult]
    gaps: list[str] = Field(default_factory=list)
    pool: list[str] = Field(default_factory=list)
    provider: str
    model: str | None = None
    verified: bool = True


class ValidationFile(BaseModel):
    provider: str
    model: str | None
    results: list[RequirementResult]


class LLMEvidence(BaseModel):
    test_id: str
    file: str
    line_start: int
    line_end: int
    quote: str


class LLMACResult(BaseModel):
    ac_id: str
    status: Status
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = ""
    evidence: list[LLMEvidence] = Field(default_factory=list)


class LLMResponse(BaseModel):
    requirement_id: str
    acs: list[LLMACResult]
    gaps: list[str] = Field(default_factory=list)
    notes: str = ""
