FROM python:3.11-slim

WORKDIR /app

# Install dbt for BigQuery
RUN pip install --no-cache-dir dbt-bigquery

# Copy dbt code
COPY . .

# Set environment variables for dbt profiles
ENV DBT_PROFILES_DIR=/app

# Execute dbt build (runs seed, run, and test in sequence)
ENTRYPOINT ["dbt", "build", "--target", "dev"]