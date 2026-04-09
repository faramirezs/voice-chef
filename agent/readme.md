## Agent

```bash
# Build the image
docker build -t voice-chef-agent-test -f Dockerfile agent

# Run the container
docker run --rm -p 8001:8001 --name voice-chef-agent-test voice-chef-agent-test

# Verify FastAPI is up
curl -i http://localhost:8001/docs

# Check logs while testing
docker logs -f voice-chef-agent-test
```

If you need to re-build just agent service:

```bash
# Slower no cache
docker compose -f docker-compose.yml -f docker-compose.override.yml build --no-cache agent
# Faster
docker compose -f docker-compose.yml -f docker-compose.override.yml build agent
# Run
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d --force-recreate agent
```


## Check with this:


```bash
curl -i -X POST http://localhost:8001/ -H "Content-Type: application/json" -d "{}"
```

AG-UI expects a specific post call:
```bash
curl -X POST http://localhost:8001/ \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -N \
  -d '{
    "threadId": "thread-001",
    "runId": "run-002",
    "state": {},
    "messages": [
      {
        "id": "msg-001",
        "role": "user",
        "content": "Hello, what is 2 + 2?"
      },
      {
        "id": "msg-002",
        "role": "assistant",
        "content": "The answer is 4."
      },
      {
        "id": "msg-003",
        "role": "user",
        "content": "And 4 + 4?"
      }
    ],
    "tools": [],
    "context": [],
    "forwardedProps": {}
  }'
  ```

You will see something like:

```bash
data: {"type":"RUN_STARTED","timestamp":1774888503747,"threadId":"thread-001","runId":"run-002"}

data: {"type":"THINKING_START","timestamp":1774888505136}

data: {"type":"THINKING_TEXT_MESSAGE_START","timestamp":1774888505136}

data: {"type":"THINKING_TEXT_MESSAGE_CONTENT","timestamp":1774888505136,"delta":"The"}...
```
