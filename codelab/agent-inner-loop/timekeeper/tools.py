"""Local tools: plain functions, no I/O, easy to test."""

CITY_ZONES = {
    "london": "Europe/London",
    "new york": "America/New_York",
    "paris": "Europe/Paris",
    "san francisco": "America/Los_Angeles",
    "singapore": "Asia/Singapore",
    "sydney": "Australia/Sydney",
    "tokyo": "Asia/Tokyo",
}


def lookup_timezone(city: str) -> dict:
    """Return the IANA time zone for a city.

    Args:
        city: A city name, for example "Tokyo".

    Returns:
        {"status": "success", "city": ..., "timezone": ...} or
        {"status": "error", "error_message": ...} for a city we don't know.
    """
    zone = CITY_ZONES.get(city.strip().lower())
    if zone is None:
        return {"status": "error", "error_message": f"No time zone on file for {city!r}."}
    return {"status": "success", "city": city, "timezone": zone}
