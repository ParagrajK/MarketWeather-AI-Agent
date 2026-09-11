from typing import Any, cast

from dotenv import load_dotenv
from agents import Agent, Runner, SQLiteSession, output_guardrail, GuardrailFunctionOutput
from fastapi import FastAPI, HTTPException
from weather_tool import get_weather
from stock_tool import get_company_stock_price
from model import AgentSummary, Guardrails, ChatRequest, ChatResponse

load_dotenv()

app = FastAPI(title="MarketWeather AI Agent", version="1.0.0")

@output_guardrail(name="Content-Monetization-Guardrail")
async def content_monetization_guardrail(
    _context: Any,
    _agent: Agent[Any],
    output: str,
) -> GuardrailFunctionOutput:
    content_checker: Agent[Any] = Agent(
        name="Content-Monetization-Agent",
        instructions="You review responses from the MarketWeather Agent and determine if they are valid according to the " \
        "defined guardrails. If the response is valid, return is_valid=True. If the response is invalid, return is_valid=False." \
        "If the response is invalid, provide a brief explanation of why it is invalid in the raw_response field." \
        "The valid response should only be related to weather and stock information. If the response contains any content related " \
        "to financial advice, investment advice, or any other content that is not related to weather and stock information, it " \
        "should be considered invalid. Personal discussions, opinions, or any other content that is not related to weather and " \
        "stock information should also be considered invalid.",
        model="gpt-5.4-mini",
        output_type=Guardrails,
    )
    agent_response: AgentSummary = cast(AgentSummary, output)
    result = await Runner.run(content_checker, agent_response.raw_response)
    guardrail_result = result.final_output
    is_valid = bool(getattr(guardrail_result, "is_valid", False))
    if is_valid:
        print("Guardrail check passed: The agent's response is valid according to the defined guardrails.")
    return GuardrailFunctionOutput(
        output_info={"guardrail": guardrail_result},
        tripwire_triggered=False,
    )

agent: Agent[Any] = Agent(
    name="MarketWeather Memory Agent",
    instructions="""
            Understand the user's intent before acting.
            - Use get_weather for current weather, temperature, rain, umbrella, raincoat, hot/cold, or similar requests.
            - Use get_company_stock_price for available stock price requests.
            - Use both tools when the user asks for both weather and stock information.
            - Never invent live data when a relevant tool is available.
            - If the user asks for information that is not available via the tools, respond with "I am sorry, I cannot provide that information."
            - Use previous conversation context to provide contextually relevant responses.
            """,
    model="gpt-5.4-mini",
    tools=[get_weather, get_company_stock_price],
    output_type=AgentSummary,
    output_guardrails=[content_monetization_guardrail]
)

async def handle_user_request(chat_request: ChatRequest):
    # Use the built-in SQLiteSession to maintain conversation history
    # This is created in-memory
    # For an on-disk memory, use SQLiteSession("12345", "memory.db")
    session = SQLiteSession(session_id=chat_request.conversation_id)
    result = await Runner.run(agent, session=session, input=chat_request.message.strip())
    return result.final_output

@app.get("/health")
async def health():
    return {"status": "ok"}

# Sample API request and response:
# Request:  
# Url: http://127.0.0.1:8000/chat
# Body: {"message": "What is the weather like in Pune?", "conversation_id": "12345"} 
#
# Response: 
# {
#    "response": {
#        "weather_report": "Current weather in Pune: overcast clouds, temperature 29.58°C, feels like 32.42°C, humidity 62%.",
#        "stock_summary": null,
#        "raw_response": "Current weather in Pune: overcast clouds, temperature 29.58°C, feels like 32.42°C, humidity 62%."
#    },
#    "conversation_id": "12345"
# }
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        agent_response: AgentSummary = await handle_user_request(request)
        return ChatResponse(
            response=agent_response,
            conversation_id=request.conversation_id,
        )
    except Exception:
        raise HTTPException(status_code=502, detail="The AI service is temporarily unavailable.")