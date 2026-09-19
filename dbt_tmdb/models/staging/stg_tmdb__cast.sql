with raw_data as (
    select
        raw_payload,
        loaded_at,
        cast(json_value(raw_payload.id) as int64) as movie_id
    from {{ source('raw_tmdb', 'movies_landed') }}
),

-- Same rule as stg_tmdb__movies: only unnest the most recent batch for each movie,
-- otherwise every cast member is repeated once per daily batch.
latest as (
    select *
    from raw_data
    where true  -- BigQuery requires WHERE, GROUP BY or HAVING alongside QUALIFY
    qualify row_number() over (partition by movie_id order by loaded_at desc) = 1
)

select
    movie_id,
    cast(json_value(cast_member.id) as int64) as actor_id,
    json_value(cast_member.name) as actor_name,
    json_value(cast_member.character) as character_name,
    cast(json_value(cast_member.order) as int64) as billing_order,
    loaded_at
from latest,
unnest(json_extract_array(raw_payload, '$.credits.cast')) as cast_member
