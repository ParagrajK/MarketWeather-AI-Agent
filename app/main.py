import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner
from weather_tool import get_weather
from stock_tool import get_company_stock_price

# Below imports are for displaying the result in a beautiful way via Markdown
# This is optional and not required for the agent to work
from rich.console import Console
from rich.markdown import Markdown

load_dotenv()

agent = Agent(
    name="MarketWeather Intent Agent",
    instructions="""
        Understand the user's intent before acting.
        - Use get_weather for current weather, temperature, rain, umbrella, raincoat, hot/cold, or similar requests.
        - Use get_company_stock_price for available stock price requests.
        - Use both tools when the user asks for both weather and stock information.
        - Never invent live data when a relevant tool is available.
        - If the user asks for information that is not available via the tools, respond with "I am sorry, I cannot provide that information."
        """,
    model="gpt-5.4-mini",
    tools=[get_weather, get_company_stock_price],
)

async def main():
    prompts = [
        "Should I carry an umbrella in Mumbai?",
        "How is Reliance doing in the market?",
    ]
    for prompt in prompts:
        result = await Runner.run(agent, prompt)
        console = Console()
        console.print(Markdown(f"\nUser: {prompt}\nAgent: {result.final_output}"))

if __name__ == "__main__":
    asyncio.run(main())
