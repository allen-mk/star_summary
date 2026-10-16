# 🌟 我的 GitHub 星标项目

> **生成时间:** {{ generated_at | format_date('%Y-%m-%d %H:%M:%S') }}
> **项目总数:** {{ stats.total_repos | format_number }}
> **分类数量:** {{ stats.category_count | format_number }}

---

## 📋 目录

{% for category_name, cat_items in grouped.items() -%}
- [{{ category_name }}](#{{ category_name }}) ({{ cat_items | length }})
{% endfor %}
---

{% for category_name, cat_items in grouped.items() -%}
## {{ category_name }}

> **项目数量:** {{ cat_items | length | format_number }}

{% for item in cat_items -%}
### [{{ item.repo.name }}]({{ item.repo.html_url }})

{% set blurb = item.classification.summary or item.repo.description -%}
{% if blurb -%}
{{ blurb }}
{% else -%}
*暂无描述*
{% endif %}

**⭐ 星标:** {{ item.repo.stargazers_count | format_number }} | **🍴 Fork:** {{ item.repo.forks_count | format_number }} | **语言:** {{ item.repo.language or '未知' }}

{% if item.repo.topics -%}
**🏷️ 标签:** {% for topic in item.repo.topics %}`{{ topic }}`{% if not loop.last %} {% endif %}{% endfor %}

{% endif -%}
{% if item.repo.homepage -%}
**🏠 主页:** [{{ item.repo.homepage }}]({{ item.repo.homepage }})

{% endif -%}
**📅 更新时间:** {{ item.repo.updated_at | format_date }}

---

{% endfor -%}
{% endfor -%}

## 📊 统计信息

### 按编程语言分布
{% for language, count in stats.language_stats.items() -%}
- **{{ language }}:** {{ count | format_number }} 个项目
{% endfor %}

### 按分类分布
{% for category, count in stats.category_stats.items() -%}
- **{{ category }}:** {{ count | format_number }} 个项目
{% endfor %}

---

*📝 本文档由 [star-summary](https://github.com/AllenHD/star-summary) 自动生成*
