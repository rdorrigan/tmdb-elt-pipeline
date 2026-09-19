FROM python:3.11-slim

WORKDIR /app

# Install dbt for BigQuery. Tighten this to the exact version you develop against
# (`pip show dbt-bigquery`), e.g. --build-arg DBT_BIGQUERY_SPEC="==1.10.2"
ARG DBT_BIGQUERY_SPEC=">=1.9,<2.0"
RUN pip install --no-cache-dir "dbt-bigquery${DBT_BIGQUERY_SPEC}"

# Copy dbt code (see .dockerignore for what is excluded)
COPY . .

# Set environment variables for dbt profiles
ENV DBT_PROFILES_DIR=/app

# Execute dbt build (runs models and tests in dependency order)
ENTRYPOINT ["dbt", "build", "--target", "dev"]
