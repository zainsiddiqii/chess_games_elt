{# Map from white_{column}, black_{column} -> my_{column}, opponent_{column} #}

{% macro map_white_black_to_my_opponent(columns_to_map, mapping_prefixes) -%}
    {% for column in columns_to_map %}
      {% for prefix in mapping_prefixes %}
        case
          when colour = 'white'
          {% if prefix == "my" %}
            then white_{{ column }}
          else black_{{ column }}
          {% else %}
            then black_{{ column }}
          else white_{{ column }}
          {% endif %}
        end as {{ prefix }}_{{ column }},
      {% endfor %}    
    {% endfor %}
{% endmacro %}