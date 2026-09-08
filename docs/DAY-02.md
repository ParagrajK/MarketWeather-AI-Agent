# Day 2/7 — Build a Multi-Tool Agent with Weather and Stock Data

## Goal

Extend the agent from a text-only assistant into a practical tool-using assistant that can answer live weather questions and retrieve stock prices from a local dataset.

In this part, we first teach the agent to call a weather tool before answering, then add a stock tool so one agent can use two tools together: one for weather and one for stock prices.

We also focus on one of the most important decisions an agent makes: choosing the right tool for the right job.

An agent may have many capabilities—weather, stock prices, news, calendars, reminders, email, search, and more. But the real challenge is not just having tools; it is deciding which tool to use based on what the user actually wants.

If the agent picks the wrong tool, it may return irrelevant data, answer the wrong question, or fail completely. This is why tool selection is a core part of building intelligent agents.

The agent should be able to answer questions like:

- What is the weather in Mumbai right now?
- Should I carry an umbrella in Pune today?
- Is it hot in Nashik compared to last week?
- What is the HDFC stock price?
- What is the Mumbai weather and HDFC stock price?

A complete multi-tool flow looks like this:

```text
                 → Weather Tool → Weather API
User → Agent ───
                 → Stock Tool → Fetch stock price from local file
```

## Why Use Tools?

The model does not know live weather by default. It only knows what it learned during training. If the user asks for current conditions or a real-time update, the agent must use a tool.

A stock tool demonstrates the same pattern with a local source instead of a remote API. Real-world agents often need to combine:

- public APIs
- internal company data
- local JSON/CSV files
- project-specific knowledge bases
- cached or offline datasets

The stock example is intentionally simple so we can focus on the agent pattern instead of stock-market logic.

> User: What is the weather in Mumbai right now?

A good agent flow looks like this:

1. Understand the user intent: this is a live weather question.
2. Recognize that the answer requires current data, not training memory.
3. Call the weather tool with the city name.
4. Return a clear answer based on the API response.

Example:

```text
User: What is the weather in Mumbai right now?

Agent: I need current data, so I will use the weather tool for Mumbai.

Weather Tool: Calls OpenWeather/Weather API and returns:
{"city": "Mumbai", "temperature_c": 29, "condition": "Cloudy", "updated_at": "2026-09-01T10:00:00Z"}

Agent: The weather in Mumbai is currently 29°C and cloudy.
```

This is different from a generic chat answer. The agent is now grounded in data from an external system.

The stock tool receives a company name, looks it up in a local file, and returns the available price. This example demonstrates how a tool can work with a local source and still be used by the same agent as the weather tool.

## What We Are Building

We are building a small agent that uses the `gpt-5.4-mini` model, a weather tool, and a stock tool. The agent will decide when a request needs external weather data, when it needs local stock data, and when it needs both.

The agent can combine multiple capabilities from different sources in one workflow:

- LLM handles reasoning and language
- Tools handle external data and actions
- The agent orchestrates both together

## Weather Tool

The weather tool is defined as a function and decorated with `@function_tool` so the agent can call it.

```python
from pydantic import BaseModel
from agents import function_tool

@function_tool
async def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: The city to query.

    Returns:
        A string description of the current weather, including temperature,
        humidity, and conditions when available.
    """
    # Step 1: validate the city
    # Step 2: call the weather API
    # Step 3: parse the response
    # Step 4: return a user-friendly result
    return "Weather data for the city"
```

This function receives a city name, calls the API, and returns a result the agent can understand and explain.

A realistic weather tool usually does the following:

```python
import os
import httpx
from agents import function_tool

@function_tool
async def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    api_key = os.getenv("WEATHER_API_KEY")
    # Implementation to get weather data goes here 
    return f"{city_name}: {temp}°C, {condition}"
    except Exception:
        return "Weather service unavailable"
```

This example shows the exact flow an agent needs:

- receive city input
- validate configuration
- call the external API
- interpret the API result
- return a clean string that the model can use in conversation

If the city is invalid, the API key is missing, or the weather service fails, the tool should return a clean error instead of a broken result. Examples:

- `City not found`
- `Weather service unavailable`
- `Invalid API key`

That lets the agent respond helpfully, such as:

> I couldn't find weather data for that city. Please check the city name.

```text
User → Agent → Weather Tool → Weather API → Live Data → Response
```

## Stock Tool

The stock tool is designed as a lightweight local-data capability. It receives a company name, reads the stock data stored in a local file inside the project directory, matches the company name, and returns the available price.

```python
@function_tool
async def get_company_stock_price(company: str) -> str:
    """Get the available stock price for the company, for example ITC."""
```

This tool does not need to be production-grade market data. The purpose is to show the architecture:

- the agent receives a user request
- it decides which tool to use
- the tool reads a local dataset
- it returns a result in a format the agent can explain back to the user

In this project, the stock data is stored in a local file inside the project directory. This is a good example of how enterprise agents can work with internal data without exposing everything to public APIs.

A common pattern looks like this:

```python
import json

with open("stocks.json") as f:
    stocks = json.load(f)
```

Then the tool can do something like:

```python
if company.lower() in stocks:
    return f"{company} stock price is {stocks[company.lower()]}"
return f"Sorry, I do not have stock data for {company}."
```

## Add Both Tools to the Agent

Once both tools are ready, attach them to the agent so the model can choose the appropriate capability automatically.

```python
from agents import Agent

agent = Agent(
    name="Weather Agent",
    instructions=(
        "You are a helpful weather and stock assistant. "
        "Use get_company_stock_price for stock price requests and get_weather for weather requests. "
    ),
    model="gpt-5.4-mini",
    tools=[get_weather, get_company_stock_price],
)
```

Pass both tools together while creating the agent

```python
tools=[get_weather, get_company_stock_price]
```

This is the key idea: one agent can expose multiple capabilities at the same time. The model decides which tool to call based on the user request, and it can even use both tools in a single answer when required.

## How the Agent Selects the Right Tool

The agent should select a tool based on the user's intent, not only on exact keywords. A simple rule such as this is tempting:

```python
if "weather" in message:
```

However, users often ask weather questions without using the word `weather`:

- Should I carry an umbrella in Mumbai?
- Is it hot in Nashik today?
- Will I need a raincoat in Pune this evening?

These requests imply a weather lookup even though they use different words. A keyword-based system can miss them or route them incorrectly. The model must understand the meaning of the request and match it to the capability provided by each tool.

The selection flow looks like this:

```text
User request and intent
            ↓
Agent instructions
            ↓
Available tool names and descriptions
            ↓
Select the most relevant tool
```

For example:

- `Is it hot in Nashik today?` → Weather tool
- `Should I carry an umbrella?` → Weather tool
- `What is the latest HDFC price?` → Stock tool
- `What is the weather in Mumbai and the HDFC stock price?` → Both tools

Tool descriptions are important because they tell the model what each capability does, when to use it, and what input it expects. A vague description makes selection harder:

```python
"""Tool for information."""
```

A useful description is specific:

```python
"""Get the current weather for a city and return its temperature and conditions."""
```

The descriptions in this project act as a contract between the tools and the agent. The weather tool handles current weather and forecast-related requests, while the stock tool handles company price lookups from the local dataset. Clear descriptions help the model route natural-language requests to the correct capability.

## Configuration

To use the weather API, you need a valid API key.

*Note: Follow [this](https://share.google/aimode/VbVlNvZLIT0Qlhxsc) guide to create 'WEATHER_API_KEY'.*

Add the key to your `.env` file:

```text
WEATHER_API_KEY=your_key
```

If the key is missing or invalid, the tool should fail gracefully and the agent should explain the issue clearly.

## Project Flow in Practice

A complete setup usually looks like this:

```text
.env
  └── WEATHER_API_KEY=... 

```text
main.py
  ├── imports model and tool definitions
  ├── creates Agent(model="gpt-5.4-mini", tools=[get_weather, get_company_stock_price])
  └── handles user prompts

weather_tool.py
  └── defines get_weather(city)

stock_tool.py
  └── defines get_company_stock_price(company)

stocks.json
  └── stores local stock prices
```

Then the user conversation may look like this:

```text
User: Should I carry an umbrella in Pune city?

Agent: I’ll check the current weather in Pune first.

Weather Tool: Pune: 26°C, Rain

Agent: It looks like it may rain in Pune right now. You should carry an umbrella.
```

A request that needs both tools can follow this flow:

```text
User: What's the weather in Pune and HDFC stock price?

Agent:
  1. Detects weather request
  2. Calls get_weather("Pune")
  3. Detects stock request
  4. Calls get_company_stock_price("HDFC")
  5. Combines both outputs into one response
```

This is exactly why multi-tool agents are useful: they can answer richer questions by combining data sources.

## Example Requests

| Request | Tool |
|---|---|
| Weather in Pune? | Weather |
| HDFC quote? | Stock |
| Mumbai weather + HDFC stock price? | Both |

## Test Cases

Test the agent directly with realistic prompts.

- Try Mumbai, Pune and Nashik.
- Try invalid city names such as `Mumbais` or `Xyz123`.
- Try a weather guidance prompt: `Should I carry umbrella in Pune city?`
- Try a missing-city prompt: `What is the weather in ?`
- Try a service failure scenario by removing or invalidating the API key.

The goal is to confirm that:

- the model calls the weather tool
- the tool returns proper data
- invalid inputs fail gracefully
- the final answer is conversational and grounded in live or local data

## Important

**Stock information is informational only and not guaranteed investment advice.** This example is for learning agent architecture, not financial guidance.

## Key Learning

This is the moment where the agent becomes dynamic and useful in the real world.

Tools allow an agent to access live systems and local data, not just respond from memory. In this project, the agent uses a weather API through a function tool to answer current questions and a stock function tool to retrieve information from a local dataset.

An agent can combine multiple capabilities from different sources in one workflow. The key idea for any agent is simple:

- LLM handles reasoning and language
- Tools handle external data and actions
- The agent orchestrates both together

That is what makes agents more than just chatbots.
