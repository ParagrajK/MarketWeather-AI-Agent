import asyncio
from typing import Any, Dict, List, cast

from dotenv import load_dotenv
from agents import Agent, Runner, SQLiteSession, output_guardrail, GuardrailFunctionOutput
from weather_tool import get_weather
from stock_tool import get_company_stock_price
from model import AgentSummary, Guardrails

load_dotenv()

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

async def main(choice: int = 1):
    if choice == 2:
        # Use the built-in SQLiteSession to maintain conversation history
        # This is created in-memory
        # For an on-disk memory, use SQLiteSession("12345", "memory.db")
        session = SQLiteSession(session_id="12345")
        print("Using built-in SQLiteSession for conversation history.")
        print("Type 'exit' to stop.")
        while True:
            message = input("\nUser: ").strip()
            if message.lower() == "exit":
                break
            if not message:
                continue

            result = await Runner.run(agent, session=session, input=message)
            print("Agent:", result.final_output)
    else:
        # Use manual conversation history management
        history: List[Dict[str, str]] = []
        print("Type 'exit' to stop.")
        while True:
            message = input("\nUser: ").strip()
            if message.lower() == "exit":
                break
            if not message:
                continue

            history.append({"role": "user", "content": message})
            result = await Runner.run(agent, cast(Any, history))
            print("Agent:", result.final_output)
            history.append({"role": "assistant", "content": result.final_output})
            print(f"\nConversation History: {history}")

if __name__ == "__main__":
    choice = input("Select choice to run agent: \n " \
    "1. Maintain manual conversation history\n " \
    "2. Agent SDK built-in SQLiteSession \n").strip().lower()
    asyncio.run(main(choice=int(choice)))