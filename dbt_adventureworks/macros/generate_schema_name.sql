{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- elif custom_schema_name == 'silver' -%}
        adventureworks_silver
    {%- elif custom_schema_name == 'gold' -%}
        adventureworks_gold
    {%- elif custom_schema_name == 'bronze' -%}
        adventureworks_bronze
    {%- else -%}
        {{ target.schema }}_{{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
