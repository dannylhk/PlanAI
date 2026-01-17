"""
Test script to verify date formatting changes
"""

from app.bot.date_utils import format_datetime, format_datetime_range

# Test cases
test_dates = [
    "2026-01-24T14:00:00",
    "2026-12-01T10:00:00",
    "2026-01-18T15:30:45",
]

print("=" * 60)
print("DATE FORMATTING TEST")
print("=" * 60)

print("\n📅 Testing format_datetime():")
print("-" * 60)
for date in test_dates:
    formatted = format_datetime(date)
    print(f"Input:  {date}")
    print(f"Output: {formatted}")
    print()

print("\n📅 Testing format_datetime_range() - Same Day:")
print("-" * 60)
start = "2026-01-24T14:00:00"
end = "2026-01-24T16:00:00"
formatted_range = format_datetime_range(start, end)
print(f"Start:  {start}")
print(f"End:    {end}")
print(f"Output: {formatted_range}")

print("\n📅 Testing format_datetime_range() - Different Days:")
print("-" * 60)
start = "2026-01-24T14:00:00"
end = "2026-01-25T16:00:00"
formatted_range = format_datetime_range(start, end)
print(f"Start:  {start}")
print(f"End:    {end}")
print(f"Output: {formatted_range}")

print("\n📅 Testing format_datetime_range() - No End Time:")
print("-" * 60)
start = "2026-01-24T14:00:00"
formatted_range = format_datetime_range(start)
print(f"Start:  {start}")
print(f"End:    None")
print(f"Output: {formatted_range}")

print("\n" + "=" * 60)
print("✅ Date formatting test completed!")
print("=" * 60)
