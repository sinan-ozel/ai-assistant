from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@tool.mcp(title="Get Current Time", read_only_hint=True)
def get_current_time(timezone: str = "UTC") -> str:
    """Return the current date and time in the specified timezone.

    Args:
        timezone: IANA timezone name, e.g. "UTC", "America/New_York", "Europe/London". Defaults to UTC.
    """
    try:
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        return (
            f"Unknown timezone: {timezone!r}. "
            "Use an IANA name such as 'UTC' or 'America/New_York'."
        )
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
