import re
from datetime import datetime, timedelta
import json


def read_json_file(file_path):
    """Reads a JSON file and returns its contents as a dictionary."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def get_current_time(relative_time_str):
    # Define a mapping of time units to timedelta
    time_units = {
        'second': 'seconds',
        'minute': 'minutes',
        'hour': 'hours',
        'day': 'days',
        'month': 'months',
        'year': 'years'
    }

    # Use regex to extract the number and the time unit (allowing for plural)
    match = re.match(r'(\d+)\s+(\w+)(s)?\s+ago', relative_time_str)
    if not match:
        raise ValueError("Invalid time format")

    quantity = int(match.group(1))
    unit = match.group(2)

    if unit.endswith("s"):
        unit = unit[:-1]

    # Convert the unit to the appropriate timedelta
    if unit in time_units:
        if unit == 'month':
            delta = timedelta(days=30 * quantity)  # Approximate month
        elif unit == 'year':
            delta = timedelta(days=365 * quantity)  # Approximate year
        else:
            delta = timedelta(**{time_units[unit]: quantity})

        # Calculate the current time
        current_time = datetime.now() - delta
        return current_time
    else:
        raise ValueError("Unsupported time unit")
