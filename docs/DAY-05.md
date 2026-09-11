# Day 5/7 — Guardrails for the MarketWeather AI Agent
## Goal

Build the guardrail layer for our MarketWeather agent using gpt-5.4-mini.

The agent already has tools, conversation handling, and structured output. Now we add boundaries around the agent so it can validate requests, handle service failures, and avoid non related prompts.

## Project Context

This series is building a small but realistic agent project:

- Model: gpt-5.4-mini
- Agent: MarketWeather Memory Agent
- Tools:
  - `get_weather`
  - `get_company_stock_price`
- Current implementation in `main.py` includes an `output_guardrail`
- `model.py` provides the `Guardrails` structured result used by the content checker

The idea is simple:

- Good requests should be processed normally.
- Bad or ambiguous requests should be rejected early.
- Tool failures should not crash the agent.

## Why this matters

Large language models are powerful, but they should not be the only validation layer around external APIs. A guardrail makes an agent's behavior explicit: accept supported requests, reject unsupported ones, and fail safely when dependencies are unavailable.

In this project, the agent is connected to real external tools. That creates risks:

- empty or whitespace-only input
- invalid or missing city names
- invalid stock symbols
- requests unrelated to weather and stock
- missing API keys or config values
- weather API timeouts or 500 errors
- stock API failures or malformed responses
- financial advice claims that are not allowed

Without guardrails, the agent may:

- hallucinate data
- call a tool incorrectly
- crash on invalid input
- leak internal errors to the user

## Problem

The current agent can receive a message, select a tool, and produce an `AgentSummary`, but not every message should reach that workflow. A blank message, an unrelated request, or a financial-advice prompt produce an answer outside the application's intended scope.

There is also a second boundary: tool output. Weather and stock services can time out, return errors, or provide malformed data. Those failures should become controlled user-facing responses rather than exceptions or invented values.

## Solution

Use guardrails at three points:

1. **Input guardrail** — validate the request before the agent and tools run.
2. **Tool boundary** — catch configuration, network, timeout, and malformed-response errors inside each tool.
3. **Output guardrail** — inspect the final structured response and block unrelated content.

### Output guardrail from `main.py`

The project uses a second agent to review the final `AgentSummary`. This keeps the review focused on the response that will actually be shown to the user:

```python
@output_guardrail(name="Content-Monetization-Guardrail")
async def content_monetization_guardrail(
  _context, _agent, output: str
) -> GuardrailFunctionOutput:
  content_checker = Agent(
    name="Content-Monetization-Agent",
    instructions=(
      "Review the MarketWeather response. It must contain only weather "
      "or stock information. Reject financial or investment advice, "
      "guarantees, and unrelated personal content. If invalid, explain "
      "why in raw_response."
    ),
    model="gpt-5.4-mini",
    output_type=Guardrails,
  )
  agent_response = cast(AgentSummary, output)
  result = await Runner.run(content_checker, agent_response.raw_response)
  decision = result.final_output
  return GuardrailFunctionOutput(
    output_info={"guardrail": decision},
    tripwire_triggered=not decision.is_valid,
  )
```

Note: I have used a second AI agent as a guardrail here, but that is not the only option. Guardrails can be implemented in multiple ways depending on your needs and the level of control you want:

- Model-based review: use a separate AI agent with specific instructions to evaluate the final response and reject disallowed content.
- Rule-based checks: scan the agent response for keywords, patterns, or unsupported intents, then reject or rewrite the output when needed.
- Deterministic validation: validate structured fields, required values, and schema constraints before returning the result.
- Tool-level safety checks: enforce input validation, configuration checks, and response-shape validation inside each tool so failures remain controlled.
- Hybrid guardrails: combine lightweight rules with a model-based reviewer for better coverage without overcomplicating the system.

The key point is that guardrails are a boundary layer, and the implementation can vary while still enforcing the same safety policy.

Register it on the agent:

```python
agent = Agent(
  name="MarketWeather Memory Agent",
  instructions="Use the weather and stock tools only for supported requests.",
  model="gpt-5.4-mini",
  tools=[get_weather, get_company_stock_price],
  output_type=AgentSummary,
  output_guardrails=[content_monetization_guardrail],
)
```

The guardrail should set `tripwire_triggered=True` when the evaluator marks the response invalid. Otherwise an invalid response is only logged in `output_info` and is not actually blocked.

## Examples

### Requests to reject before tool execution

```text
User: What is the weather in Mumbai?
Agent: Weather lookup is allowed.

User: Tell me how to double my money with TCS.
Agent: I can provide stock-price information, but not investment advice.

User: Write a poem about my weekend.
Agent: I can help only with weather and stock-price information.
```

## Use Cases

Guardrails are useful when the agent:

- calls APIs that can fail or rate-limit
- handles live market data
- serves multiple users through a CLI or API
- returns structured output consumed by another application
- must stay within a narrow product scope

They are not a replacement for authentication, authorization, secret management, rate limiting, or provider-side validation. Those controls belong around the agent as well.

## Common pattern in agent design

The guarded flow is:

```text
User request
  ↓
Input validation and scope check
  ↓
Agent selects an allowed tool
  ↓
Tool handles configuration and API failures
  ↓
Structured response
  ↓
Output safety review
  ↓
User-facing response
```

Guardrails should be observable: log the guardrail name and decision, but never log secrets or unnecessary personal data. Test both accepted and rejected paths so a future prompt or tool change does not silently weaken the boundary.

## Key Learning

A real application handles failure, not only the happy path. Input guardrails protect the workflow before execution, tool boundaries prevent dependency failures from becoming crashes, and output guardrails enforce the final safety policy before a response reaches the user.