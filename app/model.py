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