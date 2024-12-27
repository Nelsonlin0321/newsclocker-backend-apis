from typing import List
import os
import boto3
import re
from datetime import datetime, timedelta
import json
from loguru import logger


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


def sanitize_filename(filename: str) -> str:
    # Replace any character that is not alphanumeric or underscore with an underscore
    sanitized = re.sub(r'\W', '_', filename)
    return sanitized


def upload_file_to_s3(file_path, bucket_name="cloudfront-aws-bucket", s3_folder="newsclocker/insight-pdf"):

    file_name = os.path.basename(file_path)
    s3_client = boto3.client('s3')
    s3_path = os.path.join(s3_folder, file_name)

    s3_client.upload_file(file_path, bucket_name, s3_path)
    logger.info(f"Uploaded {file_path} to s3://{bucket_name}/{s3_path}")

    return f"https://d2gewc5xha837s.cloudfront.net/{s3_path}"


def convert_distance_to_now(distance_str: str) -> datetime:

    try:
        match = re.match(r'(\d+)\s+(\w+)\s+ago', distance_str)
        if match:
            value = int(match.group(1))
            unit = match.group(2).lower()

            # Map the unit to timedelta
            if unit.startswith('hour'):
                delta = timedelta(hours=value)
            elif unit.startswith('minute'):
                delta = timedelta(minutes=value)
            elif unit.startswith('second'):
                delta = timedelta(seconds=value)
            elif unit.startswith('day'):
                delta = timedelta(days=value)
            elif unit.startswith('week'):
                delta = timedelta(weeks=value)
            elif unit.startswith('month'):
                delta = timedelta(days=30*value)
            elif unit.startswith('year'):
                delta = timedelta(days=365*value)
            else:
                raise ValueError("Unsupported time unit")

            return datetime.now() - delta
        else:
            date_object = datetime.strptime(distance_str, "%d %b %Y")

            return date_object
    except Exception as e:
        logger.error(str(e))
        return datetime.now() - timedelta(weeks=1)


def process_keywords(keywords: List[str], news_sources: List[str]):
    q = " OR ".join(sorted([k.lower().strip() for k in keywords]))
    news_sources = " OR ".join(
        [f"site:{n}".lower() for n in sorted(news_sources)])
    query = q + " " + news_sources
    return query
