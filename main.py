from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent


# ============================================================
# CALCULATOR
# ============================================================

@tool
def calculator(a: float, b: float) -> str:
    """Add two numbers together."""
    return f"The sum of {a} and {b} is {a + b}"


# ============================================================
# GREETING
# ============================================================

@tool
def say_hello(name: str) -> str:
    """Greet a person by name."""
    return f"Hello {name}, I hope you are well today."


# ============================================================
# DATE & TIME
# ============================================================

@tool
def get_datetime(location: str = "Ontario") -> str:
    """
    Get the current date and time for a location.

    Examples:
    Ontario, Toronto, New York, London, Tokyo.
    """

    timezone_map = {
        "ontario": "America/Toronto",
        "toronto": "America/Toronto",
        "mississauga": "America/Toronto",
        "milton": "America/Toronto",
        "oakville": "America/Toronto",
        "hamilton": "America/Toronto",

        "new york": "America/New_York",
        "los angeles": "America/Los_Angeles",
        "chicago": "America/Chicago",

        "london": "Europe/London",
        "paris": "Europe/Paris",
        "berlin": "Europe/Berlin",

        "dubai": "Asia/Dubai",
        "abu dhabi": "Asia/Dubai",

        "tokyo": "Asia/Tokyo",
        "seoul": "Asia/Seoul",
        "singapore": "Asia/Singapore",
    }

    location_clean = location.strip().lower()

    timezone_name = timezone_map.get(location_clean)

    if timezone_name is None:
        return (
            f"I don't currently know the timezone for '{location}'. "
            f"Try a location such as Toronto, London, Dubai, or Tokyo."
        )

    try:
        current_time = datetime.now(ZoneInfo(timezone_name))

        return (
            f"The current date and time in {location.title()} is "
            f"{current_time.strftime('%A, %B %d, %Y at %I:%M:%S %p')}."
        )

    except ZoneInfoNotFoundError:
        return (
            "Timezone data is unavailable. "
            "Please make sure the 'tzdata' package is installed."
        )


# ============================================================
# WEATHER
# ============================================================

@tool
def get_weather(city: str) -> str:
    """
    Get the current weather for a city.
    Uses Open-Meteo and does not require an API key.
    """

    try:
        # ----------------------------------------------------
        # Find city coordinates
        # ----------------------------------------------------

        geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

        geocoding_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        }

        response = requests.get(
            geocoding_url,
            params=geocoding_params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("results"):
            return f"I couldn't find the city '{city}'."

        location = data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        actual_name = location.get("name", city)
        country = location.get("country", "")

        # ----------------------------------------------------
        # Get weather
        # ----------------------------------------------------

        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
            "timezone": "auto",
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10,
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()
        current = weather_data["current"]

        weather_code = current["weather_code"]

        descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Heavy rain showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail",
        }

        description = descriptions.get(
            weather_code,
            "Unknown conditions"
        )

        return (
            f"Current weather in {actual_name}, {country}:\n"
            f"Condition: {description}\n"
            f"Temperature: {current['temperature_2m']}°C\n"
            f"Feels like: {current['apparent_temperature']}°C\n"
            f"Humidity: {current['relative_humidity_2m']}%\n"
            f"Wind: {current['wind_speed_10m']} km/h"
        )

    except requests.RequestException:
        return "I couldn't connect to the weather service."

    except Exception as e:
        return f"Weather tool error: {e}"


# ============================================================
# WIKIPEDIA
# ============================================================

@tool
def wikipedia_search(topic: str) -> str:
    """
    Search Wikipedia for a topic and return a concise summary.
    """

    try:
        encoded_topic = requests.utils.quote(topic)

        url = (
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + encoded_topic
        )

        response = requests.get(
            url,
            headers={
                "User-Agent": "AI-Tool-Calling-Assistant/1.0"
            },
            timeout=10,
        )

        if response.status_code == 404:
            return f"I couldn't find a Wikipedia page for '{topic}'."

        response.raise_for_status()

        data = response.json()

        title = data.get("title", topic)
        extract = data.get("extract")

        if not extract:
            return f"I couldn't find useful information about '{topic}'."

        return (
            f"Wikipedia summary for {title}:\n"
            f"{extract}"
        )

    except requests.RequestException:
        return "I couldn't connect to Wikipedia."

    except Exception as e:
        return f"Wikipedia tool error: {e}"


# ============================================================
# MAIN
# ============================================================

def main():

    model = ChatOllama(
        model="gpt-oss:20b",
        temperature=0,
    )

    tools = [
        calculator,
        say_hello,
        get_datetime,
        get_weather,
        wikipedia_search,
    ]

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt="""
You are a helpful local AI assistant.

You have access to several tools.

Use the calculator for mathematical calculations.

Use the date/time tool whenever the user asks for
the current date, current time, today's date, or time
in a specific location.

Use the weather tool whenever the user asks about
current weather or temperature.

Use the Wikipedia tool when the user asks for factual
background information about a person, place, event,
organization, or historical topic.

Do not pretend to know live information when a tool
is available to retrieve it.

After using a tool, clearly answer the user's question.

If a tool returns an error, explain that error clearly
instead of pretending that you successfully retrieved
the information.
""",
    )

    print("=" * 60)
    print("              AI TOOL-CALLING ASSISTANT")
    print("=" * 60)

    print("\nCapabilities:")
    print("  • Mathematics")
    print("  • Unit-style numerical questions")
    print("  • Date & time")
    print("  • Weather")
    print("  • Wikipedia")
    print("  • General conversation")

    print("\nType 'quit' to exit.\n")

    while True:

        user_input = input("You: ").strip()

        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            result = agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_input,
                        }
                    ]
                }
            )

            messages = result.get("messages", [])

            # Find the final AI message
            final_response = None

            for message in reversed(messages):
                if message.type == "ai" and message.content:
                    final_response = message.content
                    break

            if final_response:
                print(f"\nAssistant: {final_response}\n")
            else:
                print(
                    "\nAssistant: I completed the request, "
                    "but I didn't receive a readable final response.\n"
                )

        except Exception as e:
            print("\nAssistant: Something went wrong.")
            print(f"Details: {e}\n")


if __name__ == "__main__":
    main()