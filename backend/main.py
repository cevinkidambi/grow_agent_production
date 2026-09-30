# backend/main.py

from typing import Any, Dict, Optional
import logging
import sys

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from .agent import root_agent, manage_user_profile
from .tools import (
    get_top_funds,
    get_fund_analysis,
    get_partner_info,
    get_visualization_data,
)

# Configure logging to stdout so Cloud Run captures it
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# =========================================================
# ADK Runner & Session Setup
# =========================================================

APP_NAME = "getu_fund_advisor_app"
DEFAULT_USER_ID = "web-user"

session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

# =========================================================
# FastAPI app
# =========================================================

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Grow Agent / GetU Advisor API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - restrict to production domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://getreksa.space",
        "https://www.getreksa.space",
        "http://localhost:3000",  # Local development
        "https://grow-agent-frontend-347225425678.us-central1.run.app",  # Cloud Run frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# Pydantic MODELS
# =========================================================


class ChatRequest(BaseModel):
    message: str
    sessionId: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    raw: Optional[Dict[str, Any]] = None


class RiskProfileRequest(BaseModel):
    answers: Dict[str, Any]
    sessionId: Optional[str] = None


# =========================================================
# HEALTHCHECK
# =========================================================

@app.get("/healthz")
def healthz():
    return {"status": "ok"}


# =========================================================
# CHAT ENDPOINT
# =========================================================

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute for chat
async def chat_endpoint(request: Request, payload: ChatRequest):
    """
    Main chat endpoint that proxies to `root_agent` via ADK Runner.
    """
    logger.info(f"[CHAT] Received message: {payload.message[:50]}..., sessionId: {payload.sessionId}")
    
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    session_id = payload.sessionId or "default-session"
    logger.info(f"[CHAT] Using session_id: {session_id}")

    # CREATE OR GET SESSION FIRST (with app_name)
    try:
        # Try to get existing session
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=DEFAULT_USER_ID,
            session_id=session_id
        )
        
        if session:
            logger.info(f"[CHAT] Found existing session: {session_id}")
        else:
            logger.info(f"[CHAT] Creating new session: {session_id}")
            await session_service.create_session(
                app_name=APP_NAME,
                user_id=DEFAULT_USER_ID,
                session_id=session_id
            )
            logger.info(f"[CHAT] Session created: {session_id}")

    except Exception as e:
        logger.error(f"[CHAT] Error managing session: {e}")
        # Attempt to create if something else went wrong
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=DEFAULT_USER_ID,
            session_id=session_id
        )

    reply_text = ""
    debug_events: list[Any] = []

    try:
        from google.genai import types as genai_types
        
        logger.info(f"[CHAT] Creating message content...")
        user_message = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=payload.message)]
        )
        
        logger.info(f"[CHAT] Starting agent run with session: {session_id}")
        
        async for event in runner.run_async(
            new_message=user_message,
            user_id=DEFAULT_USER_ID,
            session_id=session_id,
        ):
            logger.debug(f"[CHAT] Received event type: {type(event)}")
            
            # Extract text from the event content if available
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        reply_text += part.text
            
            if hasattr(event, "model_dump"):
                debug_events.append(event.model_dump())
            else:
                debug_events.append(str(event))

        logger.info(f"[CHAT] Agent run completed, reply length: {len(reply_text)}")

    except Exception as e:
        logger.error(f"[CHAT] Agent error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    if not reply_text:
        reply_text = "No response received."

    # Sanitize debug_events to ensure they are JSON serializable
    safe_debug_events = []
    for event in debug_events:
        try:
            safe_debug_events.append(str(event))
        except Exception as e:
            logger.warning(f"[CHAT] Could not serialize event: {e}")
            safe_debug_events.append("Unserializable event")

    return ChatResponse(reply=reply_text, raw={"debug_events": safe_debug_events})


# =========================================================
# FUNDS (TOP N)
# =========================================================


@app.get("/funds")
@limiter.limit("60/minute")
def list_funds(request: Request, type: str):
    """
    GET /funds?type=PU|PT|CP|SH
    """
    data = get_top_funds(type)
    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])
    return data


# =========================================================jjj
# FUND DETAIL
# =========================================================


@app.get("/funds/{fund_name}")
@limiter.limit("60/minute")
def fund_detail(request: Request, fund_name: str):
    data = get_fund_analysis(fund_name)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data


# =========================================================
# PARTNER INFO
# =========================================================


@app.get("/partners")
@limiter.limit("60/minute")
def partner_info(request: Request, name: str = "ALL"):
    """
    GET /partners?name=Bibit|Bareksa|Bank|ALL
    """
    data = get_partner_info(name)
    if isinstance(data, dict) and "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data


# =========================================================
# RISK PROFILE (HTTP + Agent memory)
# =========================================================

IN_MEMORY_PROFILES: Dict[str, Dict[str, Any]] = {}


@app.post("/risk-profile")
@limiter.limit("30/minute")
def save_risk_profile(request: Request, req: RiskProfileRequest):
    """
    POST /risk-profile { answers, sessionId }

    This stores the answers AND syncs ALL profile fields into
    the agent memory via manage_user_profile.
    """
    session_id = req.sessionId or "anonymous"
    IN_MEMORY_PROFILES[session_id] = req.answers

    # Sync ALL profile fields to agent memory (not just risk_level)
    # This allows get_user_context to access complete profile
    for key, value in req.answers.items():
        if value:  # Only save non-empty values
            manage_user_profile(
                action="save",
                key=key,  # name, risk_level, horizon, goal
                value=str(value),
                session_id=session_id,
            )

    return {"status": "ok", "sessionId": session_id}


@app.get("/risk-profile")
@limiter.limit("60/minute")
def read_risk_profile(request: Request, sessionId: str):
    # Return empty profile instead of 404 to prevent frontend crashes
    if sessionId not in IN_MEMORY_PROFILES:
        return {"sessionId": sessionId, "answers": {}}
    return {"sessionId": sessionId, "answers": IN_MEMORY_PROFILES[sessionId]}


# =========================================================
# VISUALIZATION DATA
# =========================================================


@app.get("/visualization/performance")
@limiter.limit("60/minute")
def performance_comparison(request: Request):
    data = get_visualization_data(viz_type="performance_comparison")
    if "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
    return data


@app.get("/visualization/head-to-head")
@limiter.limit("60/minute")
def head_to_head(request: Request, funds: str):
    """
    GET /visualization/head-to-head?funds=FundA,FundB
    """
    data = get_visualization_data(viz_type="head_to_head", fund_names=funds)
    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])
    return data