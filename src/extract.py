import datetime
import gzip
import io
import json
from typing import Generator

import requests

from src.storage import upload_json_lines_to_gcs
from src.tmdb_client import TMDbClient

# Only movies above this popularity in the daily ID export are fetched in detail.
POPULARITY_THRESHOLD = 15.0

# (connect, read) timeouts in seconds for the ID export download.
EXPORT_TIMEOUT = (10, 60)


def get_daily_export_url(date: datetime.date) -> str:
    date_str = date.strftime("%m_%d_%Y")
    return f"https://files.tmdb.org/p/exports/movie_ids_{date_str}.json.gz"


def stream_daily_ids(export_url: str) -> Generator[dict, None, None]:
    """Streams the gzipped, line-delimited ID export without loading it fully into memory."""
    with requests.get(export_url, stream=True, timeout=EXPORT_TIMEOUT) as response:
        response.raise_for_status()
        with gzip.GzipFile(fileobj=response.raw) as gz:
            # TextIOWrapper decodes incrementally, so multi-byte characters that
            # straddle a network chunk boundary are handled correctly, and a final
            # line without a trailing newline is still yielded.
            for line in io.TextIOWrapper(gz, encoding="utf-8"):
                line = line.strip()
                if line:
                    yield json.loads(line)


def collect_candidate_ids(export_url: str, limit: int) -> list[int]:
    """Reads the export and returns up to `limit` IDs that pass the popularity filter.

    The export download is finished (and closed) before any TMDb detail calls are
    made, so a slow API doesn't leave the export connection idling.
    """
    ids: list[int] = []
    for record in stream_daily_ids(export_url):
        if (record.get("popularity") or 0) > POPULARITY_THRESHOLD:
            ids.append(record["id"])
            if len(ids) >= limit:
                break
    return ids


def run_extraction_batch(target_date: datetime.date, limit: int = 1000):
    url = get_daily_export_url(target_date)
    client = TMDbClient()  # fail fast if credentials are missing

    print(f"Fetching daily ID export from {url}...")
    candidate_ids = collect_candidate_ids(url, limit)
    print(f"Selected {len(candidate_ids)} candidate movie IDs. Fetching details...")

    extracted_records = []
    skipped = 0
    for i, movie_id in enumerate(candidate_ids, start=1):
        movie_data = client.get_movie_details(movie_id)
        if movie_data:
            extracted_records.append(movie_data)
        else:
            skipped += 1  # 404: movie was removed since the export was built
        if i % 100 == 0:
            print(f"  fetched {i}/{len(candidate_ids)} ({skipped} not found)")

    if not extracted_records:
        # Fail the job so the workflow doesn't go on to run dbt with nothing new.
        raise RuntimeError(f"No records extracted for {target_date}; nothing to upload.")

    # Sink raw batch to GCS as NDJSON (JSON Lines). The path is deterministic, so a
    # retry or re-run for the same date overwrites the same object (idempotent).
    gcs_path = f"raw/tmdb/movies/{target_date.strftime('%Y/%m/%d')}/batch_01.json"
    upload_json_lines_to_gcs(extracted_records, gcs_path)
    print(f"Successfully staged {len(extracted_records)} raw records to {gcs_path}")
