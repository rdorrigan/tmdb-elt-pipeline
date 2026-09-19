with raw_data as (
    select
        raw_payload,
        loaded_at,
        cast(json_value(raw_payload.id) as int64) as movie_id
    from {{ source('raw_tmdb', 'movies_landed') }}
),

-- The extractor re-lands overlapping movies in every daily batch.
-- Keep only the most recent batch for each movie.
latest as (
    select *
    from raw_data
    where true  -- BigQuery requires WHERE, GROUP BY or HAVING alongside QUALIFY
    qualify row_number() over (partition by movie_id order by loaded_at desc) = 1
)

select
    movie_id,
    json_value(raw_payload.title) as title,
    -- safe_cast: TMDb returns an empty string for movies without a release date
    safe_cast(json_value(raw_payload.release_date) as date) as release_date,
    cast(json_value(raw_payload.budget) as int64) as budget_usd,
    cast(json_value(raw_payload.revenue) as int64) as revenue_usd,
    cast(json_value(raw_payload.popularity) as numeric) as popularity_score,
    cast(json_value(raw_payload.vote_average) as numeric) as vote_average,
    cast(json_value(raw_payload.vote_count) as int64) as vote_count,
    loaded_at
from latest
