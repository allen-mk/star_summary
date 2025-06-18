# 🌟 我的GitHub星标项目

> **生成时间:** {{ metadata.generated_at | format_date('%Y-%m-%d %H:%M:%S') }}  
> **项目总数:** {{ metadata.total_count | format_number }}  
> **分类数量:** {{ metadata.category_count | format_number }}  

---

## 📋 目录

{{ toc }}

---

{% for category_id, category_data in categories.items() %}
## {{ category_id | category_emoji }} {{ category_id | category_name }}

> **项目数量:** {{ category_data.repos | length | format_number }}

{% for repo in category_data.repos %}
### {{ repo.language | language_emoji }} [{{ repo.name }}]({{ repo.html_url }})

{% if repo.description %}
{{ repo.description | truncate_desc(200) }}
{% else %}
*暂无描述*
{% endif %}

**⭐ 星标:** {{ repo.stargazers_count | format_number }} | **🍴 Fork:** {{ repo.forks_count | format_number }} | **语言:** {{ repo.language or '未知' }}

{% if repo.topics %}
**🏷️ 标签:** {% for topic in repo.topics %}`{{ topic }}`{% if not loop.last %} {% endif %}{% endfor %}
{% endif %}

{% if repo.homepage %}
**🏠 主页:** [{{ repo.homepage }}]({{ repo.homepage }})
{% endif %}

**📅 更新时间:** {{ repo.updated_at | format_date }}

---

{% endfor %}

{% endfor %}

---

## 📊 统计信息

### 按编程语言分布
{% for language, count in metadata.language_stats.items() %}
- {{ language | language_emoji }} **{{ language }}:** {{ count | format_number }} 个项目
{% endfor %}

### 按分类分布
{% for category, count in metadata.category_stats.items() %}
- {{ category | category_emoji }} **{{ category | category_name }}:** {{ count | format_number }} 个项目
{% endfor %}

---

*📝 本文档由 [GitHub Star Summary](https://github.com/yourusername/star-summary) 自动生成*
