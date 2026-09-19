import os

# GCP Configurations
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "tmdb-elt-pipeline")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "tmdb-elt-raw-data")

# TMDb Configurations
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "your_tmdb_bearer_token")
TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")