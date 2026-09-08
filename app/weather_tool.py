import os
import httpx
from agents import function_tool

GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

@function_tool
async def get_weather(city: str) -> str:
    # Below is the tool description format
    # AI model knows what a tool does, when to use it, and how to format inputs for external systems
    """Get the current weather for a city using live weather data."""

    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "Weather service is not configured. WEATHER_API_KEY is missing."

    try:
        # Step 1: Get coordinates from Geocoding API
        geo_params: dict[str, str | int] = {"q": city, "limit": 1, "appid": api_key}
        with httpx.Client(timeout=10) as client:
            geo_response = client.get(GEO_URL, params=geo_params)

        if geo_response.status_code == 404:
            return f"I could not find coordinates for '{city}'."

        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data:
            return f"I could not find coordinates for '{city}'."

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        # Step 2: Get weather data using coordinates
        weather_params: dict[str, str | float] = { "lat": lat, "lon": lon, "units": "metric", "appid": api_key}
        with httpx.Client(timeout=10) as client:
            weather_response = client.get(WEATHER_URL, params=weather_params)

        if weather_response.status_code == 404:
            return f"I could not find weather information for '{city}'."

        weather_response.raise_for_status()
        data = weather_response.json()

        # Step 3: Format the weather information
        # This returns a data to LLM for final output. LLM use this data to generate a final response to user.
        return (
                    f"Current weather in {data['name']}: "
                    f"{data['weather'][0]['description']}, "
                    f"temperature {data['main']['temp']}°C, "
                    f"feels like {data['main']['feels_like']}°C, "
                    f"humidity {data['main']['humidity']}%."
                )        
    except httpx.TimeoutException:
        return "The weather service timed out. Please try again."
    except httpx.HTTPError:
        return "The weather service is temporarily unavailable."