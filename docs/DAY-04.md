# Day 4/7 — Structured Output for the Agent

## Goal

Make the agent return typed, machine-readable data instead of a plain paragraph. In this market/weather agent, the output should follow a schema that the application can trust and consume directly.

## Why this matters

Large language models are good at generating text, but most real applications need predictable data. If the agent returns a freeform paragraph, every downstream system has to interpret it manually. That leads to fragile integrations, inconsistent keys, and broken automation.

For a market/weather assistant, we need values like:

- `weather_report`
- `stock_summary`
- `raw_response`
- optional disclaimer

These fields should be stable and structured so code can consume them reliably.

## Problem

A paragraph is easy for people to read but hard for software to parse.

Examples of failure modes:

- frontend code cannot reliably read a summary from a raw string
- database inserts fail because fields are missing or inconsistent
- API clients cannot validate the result confidently
- workflows break when wording or formatting changes

This is especially risky when one tool returns weather data and another returns stock data. The output must still follow a consistent structure.

## Solution

Use Pydantic to define the exact schema that the agent must return.

```python
from typing import Optional
from pydantic import BaseModel, Field

class StockSummary(BaseModel):
    """Schema for the agent's final response."""

    company: str = Field(description="The name of the company for which the stock price is provided.")
    price: str = Field(description="The current stock price of the company.")
    disclaimer: Optional[str] = Field(
        description="Optional disclaimer for stock or financial topics."
    )

class AgentSummary(BaseModel):
    """Schema for the agent's final response."""

    weather_report: Optional[str] = Field(description="The current weather report for a specified city.")
    stock_summary: Optional[StockSummary] = Field(description="The stock summary for a specified company.")
    raw_response: str = Field(description="The raw response from the agent.")
```

This creates a contract between the model and the application. The agent is no longer allowed to return arbitrary prose; it must return data matching the schema.

## Configuration

Attach the schema to the agent with `output_type`.

```python
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
    output_type=AgentSummary,
)
```

The key idea is simple: the model returns data that matches the schema, not a freeform paragraph.

## Example: weather and stock output

```python
result = await Runner.run(agent, input="Weather in Mumbai?")
print(result.final_output)
```

Example structured response:

```json
{
  "weather_report": "The current weather in Mumbai is warm and humid with a chance of rain.",
  "stock_summary": null,
  "raw_response": "The current weather in Mumbai is warm and humid with a chance of rain."
}
```

For a company query:

```json
{
  "weather_report": null,
  "stock_summary": {
    "company": "TCS",
    "price": "₹3,480.20",
    "disclaimer": "This is informational only and not financial advice."
  },
  "raw_response": "TCS is trading at ₹3,480.20. This is informational only and not financial advice."
}
```

Now the application can access fields safely:

```python
print(result.final_output.weather_report)
print(result.final_output.stock_summary.company)
print(result.final_output.stock_summary.price)
```

## Use Cases

Structured output is useful when the agent feeds:

- JSON APIs
- frontends that render typed fields
- database records
- automation pipelines
- orchestration between tools and services

This is important for any production-grade agent that must be dependable.

## Common pattern in agent design

The standard flow is:

1. Tool or data source fetches the fact
2. LLM interprets the data and decides what it means
3. Output is validated against a schema
4. Application consumes the structured result safely

This is the stage where the agent stops being a demo and starts acting like a real application component.

## Key Learning

Humans need flexible language, but software needs predictable contracts.

For real agents, natural language is still the interface for people, but a strict schema is the contract for the application.
