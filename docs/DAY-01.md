# Day 1/7 — Project Setup and Your First AI Agent

Welcome to the first part of our AI Agent Series. In this series, we will build a practical AI-powered application called the MarketWeather AI Agent. The goal is to understand not just how to use an LLM, but how to design an agent that can reason, choose tools, fetch data, and return a useful result.

This foundation day focuses on:
- Project setup
- IDE and Python environment configuration
- Understanding Agentic AI concepts
- Building the first AI agent

---

## Series Overview

## What We Will Build

**MarketWeather AI Agent**

This project will evolve into a real AI application that can:

- 🌦️ Fetch live weather data from an external weather API
- 📈 Fetch stock information using offline/static data or a custom tool
- 🔧 Decide which tool is needed based on the user's request
- 💬 Remember short conversational context across messages
- 📦 Return structured outputs in a consistent format
- 🛡️ Handle errors and invalid requests gracefully
- 🌐 Expose functionality through a FastAPI web API
- 🚀 Deploy the app for real-world use

This is a classic Agentic AI project: the LLM is not just answering questions, it is working as a decision-making assistant with tools.

---

## Why This Series Matters

Most beginner projects focus only on chatting with an LLM. But in real-world AI applications, an agent needs to:

- understand intent
- call the right tool
- validate inputs
- process data
- respond clearly
- work with external systems

This series will teach those patterns step by step.

---

## Recommended Setup

### IDE
**Visual Studio Code (VS Code)** is recommended.

### Prerequisites
Install the following:
- VS Code
- Python 3.11+
- VS Code extensions: **Python** and **Pylance**

These tools make Python development easier, provide autocomplete, syntax checking, and a smoother coding workflow.

---

## Project Setup Instructions

### 1. Create the Project Folder
Open VS Code and create a new folder for the project.

Example structure:

```text
marketweather-ai-agent/
├── .venv/
├── .env
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── agent.py
│   ├── tools.py
│   └── models.py
├── README.md
└── .gitignore
```

We will build this structure gradually across the 7-day series.

### 2. Create a Virtual Environment
In the project terminal, run:

```bash
python -m venv .venv
```

If you have python3 installed, execute below command insted:
```bash
python3 -m venv .venv
```

This creates an isolated Python environment so dependencies do not conflict with your system Python.

### 3. Activate the Virtual Environment

**macOS/Linux**

```bash
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

You should see the terminal prompt change to include `.venv` when activation is successful.

### 4. Create `requirements.txt`
Inside the project folder, create a file named `requirements.txt` and add:

```txt
openai-agents
fastapi
uvicorn[standard]
httpx
python-dotenv
pydantic
rich
```

These dependencies are useful for:
- `openai-agents` → agent framework and orchestration
- `fastapi` → API layer
- `uvicorn` → ASGI server
- `httpx` → HTTP requests to external APIs
- `python-dotenv` → reading environment variables from `.env`
- `pydantic` → data validation and structured outputs
- `rich` → improved terminal output formatting

### 5. Install Dependencies
Run:

```bash
pip install -r requirements.txt
```

This installs all Python libraries the project needs.

### 6. Create `.env`
Create a `.env` file in the root project directory.

It will be used for sensitive values such as:
- API keys
- tokens
- environment settings

Example:

```env
OPENAI_API_KEY=your_api_key_here
WEATHER_API_KEY=your_weather_api_key_here
```

> Never commit `.env` to GitHub. Add it to `.gitignore`.

---

## What Is an AI Agent?

An AI agent is a system that does more than just generate a response. It can:

- understand the user's intention
- check whether external information is needed
- use tools or APIs
- reason about the result
- return a final answer

The basic flow looks like this:

```text
User → Agent → Decide → Tool/API → Result → Response
```

This is different from a normal chatbot flow where the model simply replies from memory or prompt context.

---

## Real Example

User asks:

> What is the weather in Mumbai right now?

Agent flow:

```text
User
 ↓
Agent identifies that live weather data is required
 ↓
Weather Tool is selected
 ↓
Weather API is called
 ↓
Live weather result is returned
 ↓
Agent converts the result into a readable answer
```

The key idea is that the agent does not guess the weather. It fetches the current data, then answers based on the real result.

---

## LLM vs AI Agent

### LLM
An LLM is a language model. It can answer questions, summarize text, rewrite content, and explain concepts.

```text
Question → Answer
```

### AI Agent
An AI agent uses an LLM but adds capabilities such as:
- tools
- memory
- decision-making
- execution flow
- structured data handling

```text
Question → Understand → Decide → Use capability (Tool) → Answer
```

### Simple Comparison

- LLM: responds based on language understanding
- Agent: acts using tools and logic

In other words, an LLM is like a skilled assistant; an agent is like a task performer with access to external systems.

---

## Core Building Blocks of an Agent

### 1. LLM
The model that understands and generates text.

### 2. Instructions / Prompt
These define how the agent behaves, what it should do, and what style of responses it should provide.

### 3. Tools
External capabilities that let the agent do real work:
- weather API calls
- database queries
- stock data lookup
- custom Python functions

### 4. Memory
Allows the agent to remember user context across multiple interactions.

### 5. Runner / Execution Layer
This orchestrates the agent flow and calls the tools in sequence.

---

## Why Tools Matter

Without tools, the model is limited to what it knows from training data. That is not enough for real-time or system-dependent tasks.

For example:
- weather needs live API data
- stock information may require a current or offline dataset
- business app tasks need database or service integration

Tools connect the LLM to the outside world.

---

## Today's Task

By the end of Day 1, we should complete these tasks:

1. Set up VS Code.
2. Create the Python environment.
3. Install dependencies.
4. Create `.env`.
5. Review the project structure.
6. Understand the difference between LLM and AI Agent.
7. Build the first AI agent.

---

## Project Goals for the Full Series

Across the next days, we will build an agent that can:
- answer weather-related queries
- answer stock-related queries
- choose the right tool automatically
- use memory for conversation continuity
- return structured outputs
- expose APIs through FastAPI
- deploy API for use in production-like environments

---

## Key Learning

```text
LLM = understands language
Instructions = behavior
Tools = external capabilities
Runner = executes the Agent
```

This foundation is essential. If we understand the pieces, we can build serious AI agents with clear logic and real-world automation.

---

## Build Your First AI Agent

Welcome to this part of our 7-part series where we are building a market and weather AI assistant from scratch. In this part, we will create our very first agent using the OpenAI Agents SDK. The goal is to understand the basic building blocks: `Agent`, `Runner`, and the model behind them.

## Goal

Create the first AI agent using `Agent` and `Runner`, and connect it to the `gpt-5.4-mini` model so it can respond to user prompts.

## Why This Matters

Before we add real tools like weather APIs or market data, we need to understand how an agent is created and executed.

At the most basic level:
- `Agent` defines the identity, instructions, and model behavior.
- `Runner` executes the agent by passing in user input.
- The model returns a response that we print or handle in Python.

This is the foundation of every AI agent we will build later in the series.

## Flow

```text
User Prompt → Agent Instructions → Model (gpt-5.4-mini) → Runner → Response
```

This flow shows how a prompt enters the system, gets processed by the agent instructions, and is sent to the model for reasoning and generation.

## Implementation

```python
from agents import Agent, Runner
from dotenv import load_dotenv
import os

load_dotenv()

agent = Agent(
	name="MarketWeather Agent",
	instructions=(
		"You are a helpful AI assistant for market and weather insights. "
		"Answer clearly, politely, and briefly."
	),
	model="gpt-5.4-mini"
)

result = Runner.run_sync(agent, "Hello! What can you do for me today?")
print(result.final_output)
```

### What each part does

- `from agents import Agent, Runner` imports the SDK classes needed to build the agent.
- `load_dotenv()` loads environment variables from `.env`.
- `Agent(...)` creates the agent, giving it a name, behavior, and model.
- `Runner.run_sync(...)` executes the agent with a user message.
- `result.final_output` stores the final text response returned by the model.

## How It Works

- `Agent` defines the role and behavior of the AI assistant.
- `Runner` handles the execution loop and user interaction.
- The model generates the response based on the prompt and agent instructions.
- `final_output` is the actual content returned to Python for display or further processing.

## Configure and Run the Agent

Before running the code, make sure your environment is ready.

### 1) Create your API key

*Note: Follow [this](https://share.google/aimode/6JECIj8VtDcxa6c7d) guide to create 'OPENAI_API_KEY'.*

### 2) Add environment variables to `.env`

```text
OPENAI_API_KEY=your_openai_key
WEATHER_API_KEY=your_key
```

> `OPENAI_API_KEY` is required for the model to respond. `WEATHER_API_KEY` is included here because this project will eventually use weather-related functionality in later parts of the series.

### 3) Run the file

```bash
python main.py
```

## Example Output

```text
Hello! I can help with market insights, weather-related questions, and general assistance. I can answer questions, explain concepts, and help with tasks in a friendly way.
```

The exact response will vary depending on the model and the prompt, but it should be a helpful and natural answer.

## Practice

Try changing the prompt in `Runner.run_sync()` and observe how the output changes.

Examples:

```python
Runner.run_sync(agent, "What is the weather in Mumbai today?")
Runner.run_sync(agent, "Give me a short summary of stock market basics.")
Runner.run_sync(agent, "Could you help me plan a trading dashboard?")
```

This helps you understand how prompt wording directly affects the model response.

## Agent Implementation Takeaways

```text
Agent = behavior
Runner = execution
Model = reasoning and response generation
```

## Session Summary

Today we focused on setup and understanding the big idea behind Agentic AI.

We learned:
- how to configure VS Code and Python
- how to create a virtual environment
- how to install project dependencies
- how to create `.env` for secrets
- what an AI agent is and how it differs from an LLM

This is the starting point for the MarketWeather AI Agent.

We then moved from setup to building the project architecture and starting the actual agent logic.

In this session, we built a minimal but working AI agent with a custom instruction set and a model. This is the first step toward creating a more powerful assistant that can use tools, access APIs, and provide useful business insight.
