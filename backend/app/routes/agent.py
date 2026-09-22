"""Agentic validation routes — wrap (never replace) the roadmap generator.

POST /api/agent/validate-roadmap   -> validate_roadmap()
POST /api/agent/apply-corrections  -> apply_corrections()
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..agent import reviser, validator

router = APIRouter(prefix="/api/agent", tags=["agent"])


class ValidateRoadmapRequest(BaseModel):
    draft_roadmap: str = Field(..., description="Draft roadmap as markdown or structured text")
    student_cv: str = Field(..., description="Student CV text")
    role_id: str = Field(..., description="Target role id, e.g. soc_analyst")


class ApplyCorrectionsRequest(BaseModel):
    draft_roadmap: str = Field(..., description="Draft roadmap as markdown or structured text")
    violations: list = Field(..., description="Violation list from validate-roadmap")


@router.post("/validate-roadmap")
async def validate_roadmap_route(body: ValidateRoadmapRequest):
    return await validator.validate_roadmap(
        body.draft_roadmap, body.student_cv, body.role_id)


@router.post("/apply-corrections")
async def apply_corrections_route(body: ApplyCorrectionsRequest):
    revised = await reviser.apply_corrections(body.draft_roadmap, body.violations)
    return {"revised_roadmap": revised}