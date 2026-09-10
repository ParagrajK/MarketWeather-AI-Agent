import asyncio
from typing import Any, Dict, List, cast

from dotenv import load_dotenv
from agents import Agent, Runner, SQLiteSession
from weather_tool import get_weather
from stock_tool import get_company_stock_price

load_dotenv()

agent = Agent(
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