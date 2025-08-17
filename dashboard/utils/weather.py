from dashboard.logger import logger
import requests

DEFAULT_CITY = "Roubaix"


def get_weather_report(city: str, version: int = 1) -> str:
    """
    Fetch the weather report for a given city and wttr.in API version (1, 2, or 3).
    """
    if version not in (1, 2, 3):
        logger.error(f"Invalid version: {version}. Must be 1, 2, or 3.")
        return "Invalid weather API version"
    try:
        response = requests.get(
            f'https://v{version}.wttr.in/{city}?F&lang=fr')
        if response.status_code == 200:
            return response.text
        else:
            logger.error(
                f"Failed to fetch weather data for {city}: {response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")


def get_minimal_weather(city: str = DEFAULT_CITY) -> str | None:
    """Fetch minimal weather data from wttr.in for small screens.

    Returns a simple format with just temperature and condition.
    """
    try:
        logger.info(f'Fetching minimal weather data for {city}')
        # Use format=3 for minimal output: "Location: condition, temperature"
        response = requests.get(
            f'https://wttr.in/{city}?format=3&lang=fr')
        if response.status_code == 200:
            weather_text = response.text.strip()
            logger.info(f"Minimal weather data fetched: {weather_text}")
            return weather_text
        else:
            logger.error(
                f'Error fetching minimal weather data status code: {response.status_code}')
            return None
    except requests.RequestException as e:
        logger.error(f"Error fetching minimal weather data: {e}")
        return None


def get_weather(city: str = DEFAULT_CITY) -> str | None:
    """Fetch the weather data from wttr.in for Roubaix.

    """
    try:
        logger.info(
            f'Fetching weather data with url : https://wttr.in/{city}?0Q&lang=fr&format=j1')
        response = requests.get(
            f'https://wttr.in/{city}?0Q&lang=fr')
        if response.status_code == 200:
            weather_text = response.text.strip()
            logger.info(response)
            return weather_text
        else:
            logger.error(
                f'Error fetching weather data status code: {response.status_code}')
    except requests.RequestException as e:
        logger.error(e)


def get_city(default_city: str = DEFAULT_CITY) -> str:
    """Return the city name for the current position.
    Returns:
        str: The city name or default_city if it cannot be determined.
    """
    try:
        response = requests.get('https://ipapi.co/json/')
        if response.status_code == 200:
            data = response.json()
            return data.get('city')
        else:
            return default_city
    except Exception as e:
        logger.error(f"Error fetching city name: {e}")
        return default_city
