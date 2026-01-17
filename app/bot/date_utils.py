"""
Date/Time Formatting Utilities
Converts ISO 8601 timestamps to human-readable format for Telegram display
NOTE: This ONLY affects display formatting, not data parsing or storage
"""

from datetime import datetime
from typing import Optional


def format_datetime(iso_string: str, timezone: str = "SGT") -> str:
    """
    Convert ISO 8601 datetime to human-readable format with timezone.
    
    Args:
        iso_string: ISO 8601 formatted string (e.g., "2026-01-24T14:00:00")
        timezone: Timezone abbreviation to display (default: "SGT" for Singapore Time)
        
    Returns:
        Formatted string: "YYYY-MM-DD HH:MM:SS SGT"
        e.g., "2026-01-24 14:00:00 SGT"
        
    Example:
        >>> format_datetime("2026-01-24T14:00:00")
        "2026-01-24 14:00:00 SGT"
    """
    if not iso_string:
        return "Not specified"
    
    try:
        # Parse ISO 8601 format
        dt = datetime.fromisoformat(iso_string)
        
        # Format as YYYY-MM-DD HH:MM:SS
        formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # Add timezone
        return f"{formatted} {timezone}"
        
    except (ValueError, AttributeError) as e:
        print(f"⚠️ Warning: Could not parse datetime '{iso_string}': {e}")
        return iso_string  # Return original if parsing fails


def format_datetime_range(start_time: str, end_time: Optional[str] = None, timezone: str = "SGT") -> str:
    """
    Format a datetime range for display.
    
    Args:
        start_time: ISO 8601 start time
        end_time: ISO 8601 end time (optional)
        timezone: Timezone abbreviation
        
    Returns:
        Formatted range string
        
    Examples:
        >>> format_datetime_range("2026-01-24T14:00:00", "2026-01-24T16:00:00")
        "2026-01-24 14:00:00 - 16:00:00 SGT"
        
        >>> format_datetime_range("2026-01-24T14:00:00")
        "2026-01-24 14:00:00 SGT"
    """
    if not start_time:
        return "Not specified"
    
    try:
        start_dt = datetime.fromisoformat(start_time)
        start_formatted = start_dt.strftime("%Y-%m-%d %H:%M:%S")
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time)
            
            # Check if same day
            if start_dt.date() == end_dt.date():
                # Same day: show date once, then time range
                end_time_only = end_dt.strftime("%H:%M:%S")
                return f"{start_formatted} - {end_time_only} {timezone}"
            else:
                # Different days: show full datetime for both
                end_formatted = end_dt.strftime("%Y-%m-%d %H:%M:%S")
                return f"{start_formatted} {timezone} - {end_formatted} {timezone}"
        else:
            # No end time
            return f"{start_formatted} {timezone}"
            
    except (ValueError, AttributeError) as e:
        print(f"⚠️ Warning: Could not parse datetime range: {e}")
        result = start_time
        if end_time:
            result += f" - {end_time}"
        return result
