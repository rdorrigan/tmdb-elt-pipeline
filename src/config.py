import os

# GCP Configurations
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "tmdb-elt-pipeline")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "tmdb-elt-raw-data")

# TMDb Configurations
TMDB_API_TOKEN = os.getenv("TMDB_ACCESS_TOKEN", "")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")