{% for category_id, category_data in categories.items() %}
- [{{ category_id | category_emoji }} {{ category_id | category_name }}](#{{ category_id | category_emoji }}-{{ category_id | category_name | lower | replace(' ', '-') | replace('/', '') }}) ({{ category_data.repos | length }})
{% endfor %}
