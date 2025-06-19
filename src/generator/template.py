"""
Jinja2模板管理器

管理和渲染Markdown模板
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound


logger = logging.getLogger(__name__)


class TemplateManager:
    """
    模板管理器
    
    负责加载、管理和渲染Jinja2模板
    """
    
    def __init__(self, template_dir: str = 'templates'):
        """
        初始化模板管理器
        
        Args:
            template_dir: 模板目录路径
        """
        self.template_dir = Path(template_dir)
        
        # 创建模板目录（如果不存在）
        self.template_dir.mkdir(exist_ok=True)
        
        # 初始化Jinja2环境
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=False,  # Markdown不需要自动转义
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # 设置自定义过滤器
        self.setup_filters()
        
        logger.info(f"模板管理器初始化完成，模板目录: {self.template_dir}")
    
    def setup_filters(self):
        """设置自定义Jinja2过滤器"""
        
        def format_date(date_value, format_string='%Y-%m-%d'):
            """格式化日期"""
            if isinstance(date_value, str):
                try:
                    # 尝试解析ISO格式日期
                    if 'T' in date_value:
                        date_value = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                    else:
                        date_value = datetime.strptime(date_value, '%Y-%m-%d')
                except ValueError:
                    return date_value
            
            if isinstance(date_value, datetime):
                return date_value.strftime(format_string)
            return str(date_value)
        
        def format_number(number):
            """格式化数字，添加千位分隔符"""
            if isinstance(number, (int, float)):
                return f"{number:,}"
            return str(number)
        
        def truncate_desc(text, length=100, suffix='...'):
            """截断描述文本"""
            if not text:
                return ""
            if len(text) <= length:
                return text
            return text[:length].rstrip() + suffix
        
        def markdown_link(text, url):
            """生成Markdown链接"""
            if not url:
                return text
            return f"[{text}]({url})"
        
        def category_display_name(category_id):
            """获取分类的显示名称"""
            # 简单的映射，实际使用时可以从CategoryManager获取
            category_names = {
                'web-frontend': 'Web前端',
                'web-backend': 'Web后端',
                'mobile': '移动开发',
                'ai-ml': 'AI/机器学习',
                'data-science': '数据科学',
                'devops': 'DevOps',
                'lang-python': 'Python',
                'lang-javascript': 'JavaScript',
                'framework': '开发框架',
                'library': '程序库',
                'tool': '开发工具',
                'uncategorized': '未分类'
            }
            return category_names.get(category_id, category_id.title())
        
        def emoji_for_category(category_id):
            """为分类添加表情符号"""
            category_emojis = {
                'web-frontend': '🎨',
                'web-backend': '⚙️',
                'mobile': '📱',
                'ai-ml': '🤖',
                'data-science': '📊',
                'devops': '🚀',
                'framework': '🏗️',
                'library': '📚',
                'tool': '🔧',
                'lang-python': '🐍',
                'lang-javascript': '🟨',
                'uncategorized': '📦'
            }
            return category_emojis.get(category_id, '📁')
        
        def language_emoji(language):
            """为编程语言添加表情符号"""
            language_emojis = {
                'Python': '🐍',
                'JavaScript': '🟨',
                'TypeScript': '🔷',
                'Java': '☕',
                'Go': '🐹',
                'Rust': '🦀',
                'C++': '⚡',
                'C#': '🔵',
                'PHP': '🐘',
                'Ruby': '💎',
                'Swift': '🍎',
                'Kotlin': '🎯',
                'Shell': '🐚'
            }
            return language_emojis.get(language, '💻')
        
        # 注册过滤器
        self.env.filters['format_date'] = format_date
        self.env.filters['format_number'] = format_number
        self.env.filters['truncate_desc'] = truncate_desc
        self.env.filters['markdown_link'] = markdown_link
        self.env.filters['category_name'] = category_display_name
        self.env.filters['category_emoji'] = emoji_for_category
        self.env.filters['language_emoji'] = language_emoji
    
    def get_template(self, template_name: str) -> Template:
        """
        获取模板对象
        
        Args:
            template_name: 模板文件名
            
        Returns:
            Jinja2模板对象
            
        Raises:
            TemplateNotFound: 模板文件不存在
        """
        try:
            return self.env.get_template(template_name)
        except TemplateNotFound:
            logger.error(f"模板文件不存在: {template_name}")
            raise
    
    def render_template(self, template_name: str, **context) -> str:
        """
        渲染模板
        
        Args:
            template_name: 模板文件名
            **context: 模板上下文变量
            
        Returns:
            渲染后的字符串
        """
        try:
            template = self.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"渲染模板 {template_name} 失败: {e}")
            raise
    
    def render_string(self, template_string: str, **context) -> str:
        """
        渲染模板字符串
        
        Args:
            template_string: 模板字符串
            **context: 模板上下文变量
            
        Returns:
            渲染后的字符串
        """
        try:
            template = self.env.from_string(template_string)
            return template.render(**context)
        except Exception as e:
            logger.error(f"渲染模板字符串失败: {e}")
            raise
    
    def list_templates(self) -> list:
        """
        列出所有可用的模板文件
        
        Returns:
            模板文件名列表
        """
        try:
            return self.env.list_templates()
        except Exception as e:
            logger.error(f"列出模板文件失败: {e}")
            return []
    
    def template_exists(self, template_name: str) -> bool:
        """
        检查模板文件是否存在
        
        Args:
            template_name: 模板文件名
            
        Returns:
            是否存在
        """
        template_path = self.template_dir / template_name
        return template_path.exists()
    
    def create_default_templates(self):
        """创建默认模板文件"""
        templates = {
            'main.md': self._get_main_template(),
            'category.md': self._get_category_template(),
            'repo_item.md': self._get_repo_item_template(),
            'toc.md': self._get_toc_template()
        }
        
        for template_name, content in templates.items():
            template_path = self.template_dir / template_name
            if not template_path.exists():
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"创建默认模板: {template_name}")
    
    def _get_main_template(self) -> str:
        """获取主文档模板"""
        return '''# 🌟 我的GitHub星标项目

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

*📝 本文档由 [GitHub Star Summary](https://github.com/AllenHD/star-summary) 自动生成*
'''
    
    def _get_category_template(self) -> str:
        """获取分类页面模板"""
        return '''# {{ category_id | category_emoji }} {{ category_id | category_name }}

> **项目数量:** {{ repos | length | format_number }}

{% for repo in repos %}
## {{ repo.language | language_emoji }} [{{ repo.name }}]({{ repo.html_url }})

{% if repo.description %}
{{ repo.description }}
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
'''
    
    def _get_repo_item_template(self) -> str:
        """获取项目条目模板"""
        return '''### {{ repo.language | language_emoji }} [{{ repo.name }}]({{ repo.html_url }})

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
'''
    
    def _get_toc_template(self) -> str:
        """获取目录模板"""
        return '''{% for category_id, category_data in categories.items() %}
- [{{ category_id | category_emoji }} {{ category_id | category_name }}](#{{ category_id | category_emoji }}-{{ category_id | category_name | lower | replace(' ', '-') | replace('/', '') }}) ({{ category_data.repos | length }})
{% endfor %}
'''
