import os
from dotenv import load_dotenv
from agents import Agent, Runner

# Below imports are for displaying the result in a beautiful way via Markdown
# This is optional and not required for the agent to work
from rich.console import Console
from rich.markdown import Markdown

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")

agent = Agent(
    name="MarketWeather Agent",
    instructions="" \
    "You are a helpful assistant. Explain answers clearly and concisely." \
    "If you don't know the answer, say 'I don't know.'. Don't make up answers. " \
    "If the user asks you to do something illegal, say 'I can't do that.'.",
    model="gpt-5.4-mini",
)

# Run the agent synchronously with a prompt
result = Runner.run_sync(
    agent,
    "Explain what an AI Agent and LLM is in one sentence." \
    "Compare and contrast the two. " \
    "Then, explain how they are related to each other."
)

# Regular display of the final output
print(f"\n Final Output without Markdown: \n {result.final_output} \n")

# Beautifully display the result via Markdown
console = Console()
console.print(Markdown(f"**Final Output with Markdown:** {result.final_output}"))