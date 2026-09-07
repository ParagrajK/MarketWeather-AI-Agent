# Day 3/7 — Add Conversation Memory to the MarketWeather Agent

## Goal

In this part, we add conversational memory so the agent can carry context across turns in the same session. This is critical when a user asks a follow-up like “What about Pune?” or “Show IBM information.” without repeating the prior topic.

We are building the AI agent using GPT-5.4-mini, and by Day 2, the agent already understands weather tools and company lookups. Now we add the memory layer that stores and reuses prior interactions.

## Why Memory Matters

Without memory, each request is treated as a brand-new conversation.

```text
User: Weather in Mumbai?
User: What about tomorrow?
```

The second question is ambiguous: “What about tomorrow?” could mean tomorrow in Mumbai, tomorrow in Pune, or something else. Without session context, the agent cannot infer the correct target.

With memory enabled, the agent can remember that the user was discussing Mumbai weather and answer appropriately.

```text
Conversation → Session → Agent → Context-aware response
```

This lets the agent maintain a thread of context across multiple user messages while still staying stateless between independent sessions.

## Architecture Change

The agent remains the same, but we pass a session object into the runner so the model can access prior messages from that conversation.

```python
session = SQLiteSession("1234")
```

This SQLite-based session persists messages and can be reused for follow-up prompts in the same conversation.

Pass it to the run call:

```python
result = await Runner.run(agent, message, session=session)
```

The key idea:

- previous turns are stored in the session
- the next message sees the conversation history
- the agent can resolve references like “Pune”, “tomorrow”, or “that company” with context

By this point, the agent is no longer just a single-prompt tool-caller; it behaves like a real conversational assistant.

## Example Conversation

```text
User: Weather in Mumbai?
Assistant: The current weather in Mumbai is ...

User: What about Pune?
Assistant: Here is the weather for Pune ...

User: Show IBM information.
Assistant: IBM is a technology company ...
```

Because the session retains prior messages, the agent can connect the user’s intent to the current thread and avoid losing topic continuity.

## Practical Implementation Notes

There are two common ways to add memory to an agent in this project.

### Approach 1: Use the built-in SQLite session

The OpenAI Agents SDK includes a session store that handles conversation state for you. You can create a session per user or conversation and then pass it directly to the runner.

```python
from agents import Runner, SQLiteSession

session = SQLiteSession("marketweather-demo")

result = await Runner.run(
    agent,
    input=message,
    session=session,
)
```

This keeps prior turns in a persistent SQLite-backed history and lets the agent resolve references like “What about Pune?” or “Show IBM information.” without requiring the user to repeat context.

Example:

```python
session = SQLiteSession("1234")
```

This gives each user or conversation its own isolated memory state while reusing the same agent logic.

### Approach 2: Manage conversation history manually

If you want more control, you can store the conversation yourself as a list of message dictionaries and pass that history into `Runner.run(...)` each turn.

```python
history = [
    {"role": "user", "content": "Weather in Mumbai?"},
    {"role": "assistant", "content": "Current weather in Mumbai is ..."},
]

history.append({"role": "user", "content": "What about Pune?"})
result = await Runner.run(agent, history)
```

In this pattern:

- you append each user message to the history
- you append the assistant response as well
- the next turn includes the full prior conversation

This works well for simple demos or cases where you want to manage memory yourself without a session store.

### Which approach should you use?

- Use `SQLiteSession` when you want built-in memory management, easy persistence, and clean conversation flow.
- Use manual history when you want full control over how messages are stored and passed to the model.

Both options are valid, and in this project we implement both patterns to understand how conversation memory works in practice.

## Test Scenarios

Ask the agent the following in sequence:

1. Weather in Mumbai?
2. What about Pune?
3. Show IBM information.
4. Compare IBM and TCS in the context of the previous requests.
5. What was the city we were discussing earlier?

Check whether the agent:

- remembers the city from the earlier message
- knows the active topic is weather or company information
- answers follow-up questions naturally instead of re-asking for context

## Important Learning

Memory is what turns a tool-calling bot into a conversational agent.

Without memory:

- each prompt is isolated
- follow-ups are ambiguous
- the user has to repeat important context

With memory:

- the agent keeps conversation continuity
- prompts become natural and user-friendly
- multi-turn interactions work the way people expect

## Key Learning

Memory provides context between requests and allows the agent to maintain continuity across the same user session. In a real-world AI agent, this is one of the foundational pieces that makes the interaction feel intelligent and useful.
