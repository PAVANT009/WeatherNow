"""English labels for Open-Meteo WMO weather interpretation codes."""

from __future__ import annotations


def describe_weather_code(code: int) -> tuple[str, str]:
    """Return an English ``(status, description)`` pair for a WMO code."""
    mapping: dict[int, tuple[str, str]] = {
        0: ("Clear", "Clear sky"), 1: ("Mostly clear", "Mostly clear sky"),
        2: ("Partly cloudy", "Partly cloudy"), 3: ("Overcast", "Overcast sky"),
        45: ("Fog", "Fog"), 48: ("Fog", "Rime fog"),
        51: ("Drizzle", "Light drizzle"), 53: ("Drizzle", "Moderate drizzle"), 55: ("Drizzle", "Dense drizzle"),
        56: ("Freezing drizzle", "Light freezing drizzle"), 57: ("Freezing drizzle", "Dense freezing drizzle"),
        61: ("Rain", "Slight rain"), 63: ("Rain", "Moderate rain"), 65: ("Rain", "Heavy rain"),
        66: ("Freezing rain", "Light freezing rain"), 67: ("Freezing rain", "Heavy freezing rain"),
        71: ("Snow", "Slight snow fall"), 73: ("Snow", "Moderate snow fall"), 75: ("Snow", "Heavy snow fall"), 77: ("Snow grains", "Snow grains"),
        80: ("Showers", "Slight rain showers"), 81: ("Showers", "Moderate rain showers"), 82: ("Showers", "Violent rain showers"),
        85: ("Snow showers", "Slight snow showers"), 86: ("Snow showers", "Heavy snow showers"),
        95: ("Thunderstorm", "Thunderstorm"), 96: ("Thunderstorm", "Thunderstorm with slight hail"), 99: ("Thunderstorm", "Thunderstorm with heavy hail"),
    }
    return mapping.get(code, ("Unknown", f"WMO weather code {code}"))
