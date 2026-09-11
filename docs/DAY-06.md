# Day 6/7 — Turn the Agent into a FastAPI Service

## Goal

In this part, the MarketWeather Agent is wrapped in FastAPI and exposed through an HTTP `POST` endpoint. The agent can now be consumed by a web application, mobile application, frontend, or another backend service.

```text
Client → POST /chat → FastAPI → Runner → Agent → Tools → External APIs → Guardrails → Response
```

## Instructions
1. Create a new file `app.py` in the same directory as `main.py`.
2. Move the existing agent logic from `main.py` into `app.py` so the application can be run as a FastAPI service.
3. Update `app.py` using the suggested refactor below. At the end of the refactor, `main.py` can be removed if you no longer need the standalone script.

## Request

```python
class ChatRequest(BaseModel):
    message: str
    conversation_id: str
```

`message` is the user's question. `conversation_id` identifies the conversation
whose history should be reused. For example, sending the same conversation ID
allows follow-up questions such as “What about tomorrow?” to use prior context.

## Response

The endpoint returns a typed response model:

```python
class ChatResponse(BaseModel):
    response: AgentSummary
    conversation_id: str
```

`response` contains the agent's structured output, including the weather report,
stock summary, and raw response. The `conversation_id` is returned so the client
can continue the same conversation in subsequent requests.

## Endpoint

```python
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        agent_response = await handle_user_request(request)
        return ChatResponse(
            response=agent_response,
            conversation_id=request.conversation_id,
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="The AI service is temporarily unavailable.",
        )
```

`handle_user_request()` is the helper that runs the agent and its tools for the incoming request:

```python
async def handle_user_request(chat_request: ChatRequest) -> AgentSummary:
    session = SQLiteSession(session_id=chat_request.conversation_id)
    result = await Runner.run(
        agent,
        session=session,
        input=chat_request.message.strip(),
    )
    return result.final_output
```

## Health Check

The service also exposes a lightweight health endpoint:

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

## Run

Start the development server from /app directory (Not inside root project directory):

```bash
uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

FastAPI automatically generates interactive Swagger documentation at `/docs`.

## Test

Request:

```json
{
  "message": "What is the weather like in Pune?",
  "conversation_id": "12345"
}
```

Response:

```json
{
  "response": {
    "weather_report": "Current weather in Pune: overcast clouds, temperature 29.58°C, feels like 32.42°C, humidity 62%.",
    "stock_summary": null,
    "raw_response": "Current weather in Pune: overcast clouds, temperature 29.58°C, feels like 32.42°C, humidity 62%."
  },
  "conversation_id": "12345"
}
```

Example using `curl`:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the weather in Mumbai?","conversation_id":"mumbai-demo"}'
```

## Request Flow

1. FastAPI validates the JSON body against `ChatRequest`.
2. `chat()` forwards the validated request to `handle_user_request()`.
3. `handle_user_request()` creates a `SQLiteSession` for the provided `conversation_id` and runs the agent with `Runner.run()`.
4. The agent calls `get_weather` and/or `get_company_stock_price` when needed.
5. The output is checked by the content-monetization guardrail.
6. FastAPI returns the typed `ChatResponse` as JSON.

Unexpected service or upstream failures are returned as HTTP `502` instead of exposing internal exception details to the client.

## Key Learning

The agent is now exposed as a typed, validated HTTP service. FastAPI handles request validation and transport, while the agent remains responsible for reasoning, tool selection, conversation context, and guarded structured output.
