import json
from http import HTTPStatus
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from pydantic_ai.ui import SSE_CONTENT_TYPE
from pydantic_ai.ui.ag_ui import AGUIAdapter
from .agent import agent  # ← import the agent defined in agent.py


# Create the main FastAPI application for this service.
app = FastAPI()

# Enable very permissive CORS so local frontends can call this service.
# For production, replace "*" with specific trusted origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
async def run_agent(request: Request) -> Response:
    return await AGUIAdapter.dispatch_request(request, agent=agent)

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
