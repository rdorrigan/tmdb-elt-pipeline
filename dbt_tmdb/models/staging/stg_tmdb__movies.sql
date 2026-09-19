with raw_data as (
    select 
        raw_payload,
        loaded_at
    from {{ source('raw_tmdb', 'movies_landed') }}
)

select
    cast(json_value(raw_payload.id) as int64) as movie_id,
    json_value(raw_payload.title) as title,
    cast(json_value(raw_payload.release_date) as date) as release_date,
    cast(json_value(raw_payload.budget) as int64) as budget_usd,
    cast(json_value(raw_payload.revenue) as int64) as revenue_usd,
    cast(json_value(raw_payload.popularity) as numeric) as popularity_score,
    cast(json_value(raw_payload.vote_average) as numeric) as vote_average,
    cast(json_value(raw_payload.vote_count) as int64) as vote_count,
    loaded_at
from raw_data