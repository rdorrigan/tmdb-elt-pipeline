import zlib
import gzip
import json
import datetime
import requests
from typing import Generator
from src.tmdb_client import TMDbClient
from src.storage import upload_json_lines_to_gcs

def get_daily_export_url(date: datetime.date) -> str:
    date_str = date.strftime("%m_%d_%Y")
    return f"https://files.tmdb.org/p/exports/movie_ids_{date_str}.json.gz"

def stream_daily_ids(export_url: str) -> Generator[dict, None, None]:
    """Streams gzipped line-delimited JSON without loading full file to RAM."""
    response = requests.get(export_url, stream=True)
    response.raise_for_status()
    
    d = zlib.decompressobj(wbits=zlib.MAX_WBITS | 32)
    buffer = ""
    
    for chunk in response.iter_content(chunk_size=65536):
        decompressed = d.decompress(chunk).decode('utf-8', errors='ignore')
        buffer += decompressed
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            if line.strip():
                yield json.loads(line)

def run_extraction_batch(target_date: datetime.date, limit: int = 1000):
    url = get_daily_export_url(target_date)
    client = TMDbClient()
    
    extracted_records = []
    print(f"Fetching daily ID export from {url}...")
    
    for record in stream_daily_ids(url):
        # Filter for high popularity or target criteria to limit initial extraction
        if record.get("popularity", 0) > 15.0:
            movie_data = client.get_movie_details(record["id"])
            if movie_data:
                extracted_records.append(movie_data)
            
            if len(extracted_records) >= limit:
                break
                
    # Sink raw batch to GCS as NDJSON (JSON Lines)
    gcs_path = f"raw/tmdb/movies/{target_date.strftime('%Y/%m/%d')}/batch_01.json"
    upload_json_lines_to_gcs(extracted_records, gcs_path)
    print(f"Successfully staged {len(extracted_records)} raw records to {gcs_path}")