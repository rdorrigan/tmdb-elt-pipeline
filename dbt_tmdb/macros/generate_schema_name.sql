{#
  dbt's default appends a model's custom schema to the profile's dataset
  (e.g. tmdb_staging + staging -> tmdb_staging_staging). This override uses the
  custom schema exactly as written, and falls back to the profile dataset when a
  model doesn't set one.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
