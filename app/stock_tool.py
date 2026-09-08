from agents import function_tool
import json
from pathlib import Path

@function_tool
async def get_company_stock_price(company: str) -> str:
    """Get the available stock price for the company, for example ITC."""

    # Open and load the local JSON file
    file_path = Path(__file__).parent / 'stocks.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        data: dict[str, float] = json.load(file)

    # Find all companies that contain the company name (case-insensitive)
    matching_keys = [key for key in data.keys() if company.lower() in key.lower()]

    stock_prices = {key: data[key] for key in matching_keys}
    if not stock_prices:
        return f"No stock prices found for companies matching '{company}'."
    else:
        return f"Available stock prices for companies matching '{company}': {stock_prices}"
    
