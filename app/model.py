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

class Guardrails(BaseModel):
    """Schema for the agent's final response."""

    is_valid: bool = Field(description="Indicates whether the agent's request / response is valid according to the defined guardrails.")

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    conversation_id: str = Field(description="Conversation ID for context.")

class ChatResponse(BaseModel):
    response: AgentSummary = Field(description="The agent's final response.")
    conversation_id: str = Field(description="Conversation ID for context.")