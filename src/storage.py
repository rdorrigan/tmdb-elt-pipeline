import json
from google.cloud import storage
from src.config import GCS_BUCKET_NAME, GCP_PROJECT_ID

def upload_json_lines_to_gcs(records: list[dict], destination_blob_name: str) -> None:
    """Writes a list of Python dictionaries to GCS as line-delimited JSON (NDJSON)."""
    if not records:
        print("No records provided to upload.")
        return

    # Initialize GCS client
    client = storage.Client(project=GCP_PROJECT_ID)
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    # Format output as NDJSON
    ndjson_data = "\n".join([json.dumps(record) for record in records])

    blob.upload_from_string(ndjson_data, content_type="application/x-ndjson")
    print(f"Successfully uploaded {len(records)} records to gs://{GCS_BUCKET_NAME}/{destination_blob_name}")