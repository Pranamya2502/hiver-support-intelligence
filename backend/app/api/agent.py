from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.services.agent import SupportAgent


router = APIRouter(prefix="/agent", tags=["agent"])

agent = SupportAgent()


class AgentRequest(BaseModel):
    customer_message: str


@router.post("/respond")
def respond(request: AgentRequest):
    try:
        return agent.handle(request.customer_message)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))