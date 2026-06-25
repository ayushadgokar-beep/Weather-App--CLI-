import os
import requests
from datetime import datetime
from config import API_KEY, BASE_URL

# ──────────────────────────────────────────────────────────
# Optional: colorama for colourful terminal output.
# If not installed the app works fine — just without colour.
# Install with:  pip install colorama
# ──────────────────────────────────────────────────────────
try:
    from colorama import init, Fore, Style
    init(autoreset=True)          # Reset colour automatically after each print
    CLR = {
        "cyan":    Fore.CYAN,
        "yellow":  Fore.YELLOW,
        "green":   Fore.GREEN,
        "white":   Fore.WHITE,
        "red":     Fore.RED,
        "magenta": Fore.MAGENTA,
        "bold":    Style.BRIGHT,
        "reset":   Style.RESET_ALL,
    }
except ImportError:
    # Fallback: empty strings so all f-strings still work unchanged
    CLR = {k: "" for k in ["cyan", "yellow", "green", "white",
                            "red", "magenta", "bold", "reset"]}


# ──────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────

SEP = "=" * 46   # Separator line used in headers

# Always save last_city.txt next to this script file
SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
LAST_CITY_FILE = os.path.join(SCRIPT_DIR, "last_city.txt")

# Maps substrings in weather descriptions → display emojis
WEATHER_EMOJIS = {
    "clear":        "☀️",
    "few clouds":   "🌤️",
    "scattered":    "⛅",
    "broken":       "🌥️",
    "overcast":     "☁️",
    "light rain":   "🌦️",
    "drizzle":      "🌦️",
    "rain":         "🌧️",
    "thunderstorm": "⛈️",
    "snow":         "❄️",
    "sleet":        "🌨️",
    "mist":         "🌫️",
    "fog":          "🌫️",
    "haze":         "🌫️",
    "smoke":        "🌫️",
    "dust":         "🌪️",
    "tornado":      "🌪️",
}


# ──────────────────────────────────────────────────────────
# Utility / Helper Functions
# ──────────────────────────────────────────────────────────

def get_emoji(condition: str) -> str:
    """
    Return the best-matching weather emoji for a condition string.
    Scans WEATHER_EMOJIS for the first keyword found in `condition`.
    Falls back to 🌡️ if nothing matches.
    """
    condition_lc = condition.lower()
    for keyword, emoji in WEATHER_EMOJIS.items():
        if keyword in condition_lc:
            return emoji
    return "🌡️"


def print_header() -> None:
    """Display the top banner when the app starts."""
    print(f"\n{CLR['cyan']}{SEP}")
    print(f"{CLR['yellow']}           🌤️  Weather App  🌤️")
    print(f"{CLR['cyan']}{SEP}")


def print_error(message: str) -> None:
    """Display a red error message with a consistent format."""
    print(f"\n{CLR['red']}  ❌  {message}\n")


# ──────────────────────────────────────────────────────────
# Last-City Persistence  (Bonus Feature)
# ──────────────────────────────────────────────────────────

def save_last_city(city: str) -> None:
    """
    Write the city name to last_city.txt so it can be suggested
    the next time the app is launched.
    """
    try:
        with open(LAST_CITY_FILE, "w", encoding="utf-8") as f:
            f.write(city)
    except OSError:
        pass   # Not critical — silently ignore file errors


def load_last_city() -> str:
    """
    Read the last searched city from file.
    Returns an empty string if the file doesn't exist yet.
    """
    try:
        with open(LAST_CITY_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except (OSError, FileNotFoundError):
        return ""


# ──────────────────────────────────────────────────────────
# API Functions
# ──────────────────────────────────────────────────────────

def fetch_weather(city: str) -> requests.Response:
    """
    Call the OpenWeatherMap current-weather endpoint.

    Args:
        city : City name typed by the user.

    Returns:
        requests.Response — callers must check .status_code.

    Raises:
        requests.exceptions.ConnectionError : No internet / DNS failure.
        requests.exceptions.Timeout         : Server didn't respond in time.
        requests.exceptions.RequestException: Any other network error.
    """
    params = {
        "q":     city,
        "appid": API_KEY,
        "units": "metric",   # Use "imperial" here for °F instead of °C
    }
    return requests.get(BASE_URL, params=params, timeout=10)


def parse_weather(api_data: dict) -> dict:
    """
    Extract and format the fields we need from the raw API JSON response.

    Args:
        api_data : Parsed JSON dictionary from a 200-OK API response.

    Returns:
        A clean dictionary ready to be passed to display_weather().
    """
    # Sunrise / sunset come as Unix timestamps — convert to readable time
    sunrise = datetime.fromtimestamp(api_data["sys"]["sunrise"]).strftime("%I:%M %p")
    sunset  = datetime.fromtimestamp(api_data["sys"]["sunset"]).strftime("%I:%M %p")

    # Visibility is in metres; convert to kilometres for readability
    vis_m   = api_data.get("visibility")          # .get() avoids KeyError if missing
    vis_str = f"{vis_m / 1000:.1f} km" if vis_m is not None else "N/A"

    return {
        "city":       api_data["name"],
        "country":    api_data["sys"]["country"],
        "temp":       round(api_data["main"]["temp"],       1),
        "feels_like": round(api_data["main"]["feels_like"], 1),
        "temp_min":   round(api_data["main"]["temp_min"],   1),
        "temp_max":   round(api_data["main"]["temp_max"],   1),
        "condition":  api_data["weather"][0]["description"].title(),
        "humidity":   api_data["main"]["humidity"],
        "wind_speed": api_data["wind"]["speed"],
        "pressure":   api_data["main"]["pressure"],
        "visibility": vis_str,
        "sunrise":    sunrise,
        "sunset":     sunset,
    }


# ──────────────────────────────────────────────────────────
# Display Function
# ──────────────────────────────────────────────────────────

def display_weather(w: dict) -> None:
    """
    Print all weather information in a neatly formatted, emoji-rich layout.

    Args:
        w : Dictionary returned by parse_weather().
    """
    emoji = get_emoji(w["condition"])
    now   = datetime.now().strftime("%A, %d %B %Y  |  %I:%M %p")

    # ── Section: Timestamp header ──────────────────
    print(f"\n{CLR['cyan']}{SEP}")
    print(f"{CLR['green']}  🕒  {now}")
    print(f"{CLR['cyan']}{SEP}")

    # ── Section: Location ──────────────────────────
    print(f"{CLR['white']}  📍  City        : {CLR['bold']}{w['city']}, {w['country']}")

    # ── Section: Temperature ───────────────────────
    print(f"{CLR['white']}  🌡️   Temperature : {CLR['yellow']}{w['temp']}°C")
    print(f"{CLR['white']}  🤔  Feels Like  : {w['feels_like']}°C")
    print(f"{CLR['white']}  🔼  High / Low  : {w['temp_max']}°C  /  {w['temp_min']}°C")

    # ── Section: Sky Condition ─────────────────────
    print(f"{CLR['white']}  {emoji}  Condition   : {w['condition']}")

    # ── Section: Atmosphere ────────────────────────
    print(f"{CLR['white']}  💧  Humidity    : {w['humidity']}%")
    print(f"{CLR['white']}  💨  Wind Speed  : {w['wind_speed']} m/s")
    print(f"{CLR['white']}  📊  Pressure    : {w['pressure']} hPa")
    print(f"{CLR['white']}  👁️   Visibility  : {w['visibility']}")

    # ── Section: Sun times ─────────────────────────
    print(f"{CLR['white']}  🌅  Sunrise     : {w['sunrise']}")
    print(f"{CLR['white']}  🌇  Sunset      : {w['sunset']}")

    print(f"{CLR['cyan']}{SEP}\n")


# ──────────────────────────────────────────────────────────
# Main Application Loop
# ──────────────────────────────────────────────────────────

def main() -> None:
    """
    Entry point for the Weather App.
    Displays the header and runs an infinite city-search loop
    until the user chooses to exit.
    """
    print_header()

    # Load the last searched city from a previous session
    last_city = load_last_city()
    if last_city:
        print(f"{CLR['magenta']}  💾  Last searched: {last_city}")

    while True:

        # ── Step 1: Get a city name from the user ──────
        print()
        if last_city:
            # Offer to re-use the previous city with a blank Enter
            prompt = f"  Enter city name (or Enter for '{last_city}'): "
        else:
            prompt = "  Enter city name: "

        city = input(prompt).strip()

        # If the user pressed Enter without typing, reuse last city
        if not city:
            if last_city:
                city = last_city
            else:
                print_error("Please enter a city name.")
                continue

        # ── Step 2: Fetch weather from the API ─────────
        try:
            response = fetch_weather(city)

            # ── Success ────────────────────────────────
            if response.status_code == 200:
                weather = parse_weather(response.json())
                display_weather(weather)
                # Save the API-capitalised name, not the user's raw input
                save_last_city(weather["city"])
                last_city = weather["city"]

            # ── City not found ─────────────────────────
            elif response.status_code == 404:
                print_error(
                    "City not found.\n"
                    "     Please enter a valid city name."
                )

            # ── Bad API key ────────────────────────────
            elif response.status_code == 401:
                print_error(
                    "Invalid API key.\n"
                    "     1. Open config.py\n"
                    "     2. Replace 'your_api_key_here' with your actual key\n"
                    "     3. Get a free key at: https://openweathermap.org/api\n"
                    "     Note: New keys can take up to 10 minutes to activate."
                )
                break   # No point continuing with a bad key

            # ── Rate limited ───────────────────────────
            elif response.status_code == 429:
                print_error("Rate limit reached. Please wait a moment and try again.")

            # ── Other HTTP errors ──────────────────────
            else:
                print_error(f"Unexpected server error (HTTP {response.status_code}).")

        # ── No internet connection ─────────────────────
        except requests.exceptions.ConnectionError:
            print_error(
                "Unable to connect to the weather server.\n"
                "     Please check your internet connection."
            )

        # ── Request timed out ──────────────────────────
        except requests.exceptions.Timeout:
            print_error(
                "The request timed out.\n"
                "     The server took too long to respond. Please try again."
            )

        # ── Any other network error ────────────────────
        except requests.exceptions.RequestException as exc:
            print_error(f"An unexpected network error occurred:\n     {exc}")

        # ── Step 3: Ask whether to search again ────────
        print()
        choice = input(
            f"  {CLR['cyan']}Would you like to search another city? (y/n): {CLR['reset']}"
        ).strip().lower()

        if choice != "y":
            print(f"\n{CLR['yellow']}  👋  Thank you for using Weather App! Goodbye!")
            print(f"{CLR['cyan']}{SEP}\n")
            break


# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
