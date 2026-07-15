import re
from datetime import datetime

import dateparser

_TIME_PATTERN = re.compile(
    r'(?:'
    r'\d{1,2}\s*[:.]\s*\d{2}|'
    r'(?:полдень|полночь|noon|midnight)|'
    r'(?:через|in)\s+\d+\s*(?:мин|minute|hour|час|минут|минуты|минуту|часа|часов|hours?|minutes?)?|'
    r'\d{1,2}\s*(?:am|pm)'
    r')',
    re.IGNORECASE,
)

_MAX_DATETIME_TOKENS = 4

def _has_time(candidate: str) -> bool:
    return bool(_TIME_PATTERN.search(candidate))

def parse_reminder_input(text: str, timezone: str = 'UTC') -> tuple[datetime, str] | None:
    parts = text.strip().split()
    if len(parts) < 2:
        return None

    settings = {
        'PREFER_DATES_FROM': 'future',
        'TIMEZONE': timezone,
        'RETURN_AS_TIMEZONE_AWARE': False,
    }

    max_end = min(_MAX_DATETIME_TOKENS, len(parts) - 1)
    for end in range(max_end, 0, -1):
        candidate = ' '.join(parts[:end])
        remainder = ' '.join(parts[end:]).strip()
        if not remainder or not _has_time(candidate):
            continue

        parsed = dateparser.parse(candidate, languages=['ru', 'en'], settings=settings)
        if parsed:
            return parsed, remainder

    return None