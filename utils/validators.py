from datetime import datetime

def is_valid_date(date_string: str) -> bool:
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def is_valid_time(time_string: str) -> bool:
    try:
        datetime.strptime(time_string, '%H:%M')
        return True
    except ValueError:
        return False