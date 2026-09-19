-- Run once (and again whenever this file changes). Keeping it in the repo means
-- the raw layer can be rebuilt from scratch.

-- 1) External table: each line of every NDJSON file is read as one STRING.
--    (format NEWLINE_DELIMITED_JSON would map top-level keys to columns and fail
--    with "No such field: adult"). json.dumps() escapes control characters, so
--    \x1b can never appear inside a line; quote = '' stops the JSON's own double
--    quotes from being treated as CSV quoting.
CREATE OR REPLACE EXTERNAL TABLE `tmdb-elt-pipeline.tmdb_raw.movies_landed_lines` (
    raw_line STRING
)
OPTIONS (
    format = 'CSV',
    uris = ['gs://tmdb-elt-raw-data/raw/tmdb/movies/*'],
    field_delimiter = '\x1b',
    quote = '',
    allow_quoted_newlines = FALSE
);

-- 2) View that dbt reads as source('raw_tmdb', 'movies_landed').
--    _FILE_NAME only exists on the external table, so everything derived from it
--    has to be exposed here.
CREATE OR REPLACE VIEW `tmdb-elt-pipeline.tmdb_raw.movies_landed` AS
SELECT
    SAFE.PARSE_JSON(raw_line) AS raw_payload,   -- NULL if a line is malformed
    raw_line,
    _FILE_NAME AS source_file,
    PARSE_DATE(
        '%Y/%m/%d',
        REGEXP_EXTRACT(_FILE_NAME, r'/movies/(\d{4}/\d{2}/\d{2})/')
    ) AS loaded_at                              -- batch date from the GCS path
FROM `tmdb-elt-pipeline.tmdb_raw.movies_landed_lines`;
