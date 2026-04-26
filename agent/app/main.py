import json
import os
import time
import logging
from http import HTTPStatus
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic_ai.ui.ag_ui import AGUIAdapter
from pydantic_ai.usage import UsageLimits
from .agent import agent  # ← import the agent defined in agent.py
from .state import KitchenState
from pydantic_ai.ui import StateDeps


logger = logging.getLogger("voice-chef.agent")
DEBUG_STREAM = os.getenv("AGENT_DEBUG_STREAM", "0") == "1"


# Create the main FastAPI application for this service.
app = FastAPI()

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

# CORS (Cross-Origin Resource Sharing) is a browser security mechanism that controls
# whether a web page can make requests to a different domain (origin) than the one
# it was loaded from.
# CORS configuration driven by environment (dev/prod).
# Credentials enabled → explicit origins required (no "*").
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/")
async def run_agent(request: Request) -> Response:
    started = time.perf_counter()
    if DEBUG_STREAM:
        logger.warning(
            "[agent-debug] request:start accept=%s content-type=%s user-agent=%s",
            request.headers.get("accept"),
            request.headers.get("content-type"),
            request.headers.get("user-agent"),
        )

    response = await AGUIAdapter.dispatch_request(
        request,
        agent=agent,
        deps=StateDeps(state=KitchenState()),
        usage_limits=UsageLimits(request_limit=25, tool_calls_limit=10),
    )

    if DEBUG_STREAM:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.warning(
            "[agent-debug] request:end status=%s media_type=%s elapsed_ms=%s",
            response.status_code,
            response.media_type,
            elapsed_ms,
        )

    return response
