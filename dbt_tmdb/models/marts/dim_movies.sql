with movies as (
    select * from {{ ref('stg_tmdb__movies') }}
),

cast_summary as (
    select
        movie_id,
        count(distinct actor_id) as total_cast_members,
        string_agg(actor_name, ', ' order by billing_order asc limit 3) as top_billed_actors
    from {{ ref('stg_tmdb__cast') }}
    group by 1
)

select
    m.movie_id,
    m.title,
    m.release_date,
    extract(year from m.release_date) as release_year,
    m.budget_usd,
    m.revenue_usd,
    case 
        when m.budget_usd > 0 then round((m.revenue_usd - m.budget_usd) / m.budget_usd, 4)
        else null 
    end as return_on_investment,
    m.popularity_score,
    m.vote_average,
    m.vote_count,
    coalesce(c.total_cast_members, 0) as total_cast_members,
    c.top_billed_actors,
    m.loaded_at as pipeline_updated_at
from movies m
left join cast_summary c on m.movie_id = c.movie_id