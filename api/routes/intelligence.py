"""Intelligence API routes — morning briefs, stock alerts, demand forecasts."""

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.services.intelligence_service import generate_morning_brief
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()


class MorningBriefRequest(BaseModel):
    merchant_id: str
    language: str = "hi"


@router.post("/intelligence/morning-brief")
async def get_morning_brief(req: MorningBriefRequest):
    """Generate morning brief for a merchant.

    Returns business stats, stock alerts, demand forecast, and suggestions.
    """
    try:
        brief = generate_morning_brief(req.merchant_id, req.language)
        return {
            "status": "success",
            "data": brief,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate morning brief: {str(e)}")


@router.get("/intelligence/morning-brief/{merchant_id}")
async def get_morning_brief_simple(merchant_id: str, language: str = "hi"):
    """Generate morning brief for a merchant (GET version for easy testing)."""
    try:
        brief = generate_morning_brief(merchant_id, language)
        return {
            "status": "success",
            "data": brief,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate morning brief: {str(e)}")
