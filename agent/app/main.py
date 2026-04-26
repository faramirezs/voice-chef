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
from .agent import agent  # ← import the agent defined in agent.py


logger = logging.getLogger("voice-chef.agent")
DEBUG_STREAM = os.getenv("AGENT_DEBUG_STREAM", "0") == "1"


# Create the main FastAPI application for this service.
app = FastAPI()

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174").split(",")

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

    response = await AGUIAdapter.dispatch_request(request, agent=agent)

    if DEBUG_STREAM:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.warning(
            "[agent-debug] request:end status=%s media_type=%s elapsed_ms=%s",
            response.status_code,
            response.media_type,
            elapsed_ms,
        )

    return response

# @app.post("/")
# async def run_agent(request: Request) -> Response:
#     accept = request.headers.get("accept", SSE_CONTENT_TYPE)
#     try:
#         # Parse the raw request body into a typed RunAgentInput object.
#         # Raises ValidationError if any required field (threadId, messages, etc.) is missing.
#         run_input = AGUIAdapter.build_run_input(await request.body())
#     except ValidationError as e:
#         # Return a 422 with the list of field errors so the client knows what's wrong.
#         return Response(
#             content=json.dumps(e.errors()),
#             media_type="application/json",
#             status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
#         )
#     adapter = AGUIAdapter(agent=agent, run_input=run_input, accept=accept)
#     # adapter.stream() runs the agent and yields AG-UI events as an async generator.
#     # streaming_response() wraps that generator into an SSE HTTP response.
#     return adapter.streaming_response(adapter.run_stream())

# @app.post("/agent")
# async def run_agent(body: RunAgentInput):
#     handler = AGUIHandler(agent=agent, input=body)
#     return StreamingResponse(
#         handler.stream(),
#         media_type="text/event-stream",
#     )

# Build an AG-UI compatible ASGI app directly from the agent.
# This is the recommended high-level integration for pydantic-ai 1.73.0.
# ag_ui_app = agent.to_ag_ui()

# Mount the AG-UI app at /agent.
# Requests to /agent/* are handled by the mounted AG-UI application.
# app.mount("/agent", ag_ui_app)
