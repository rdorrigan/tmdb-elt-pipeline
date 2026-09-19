with raw_data as (
    select raw_payload from {{ source('raw_tmdb', 'movies_landed') }}
)

select
    cast(json_value(raw_payload.id) as int64) as movie_id,
    cast(json_value(cast_member.id) as int64) as actor_id,
    json_value(cast_member.name) as actor_name,
    json_value(cast_member.character) as character_name,
    cast(json_value(cast_member.order) as int64) as billing_order
from raw_data,
unnest(json_extract_array(raw_payload, '$.credits.cast')) as cast_member