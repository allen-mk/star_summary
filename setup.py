"""
GitHub 星标项目分类整理工具 - 安装配置
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README文件
this_directory = Path(__file__).parent
try:
    long_description = (this_directory / "README.md").read_text(encoding='utf-8')
except FileNotFoundError:
    # 如果README.md不存在，回退到TOOL_README.md
    try:
        long_description = (this_directory / "TOOL_README.md").read_text(encoding='utf-8')
    except FileNotFoundError:
        long_description = "GitHub 星标项目分类整理工具"

# 读取requirements.txt
def parse_requirements(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f 
                if line.strip() and not line.startswith('#')]

# 核心依赖（排除开发依赖）
install_requires = [
    "PyGithub>=1.59.1",
    "PyYAML>=6.0",
    "python-dotenv>=1.0.0",
    "click>=8.1.7",
    "Jinja2>=3.1.2",
    "tqdm>=4.66.0",
    "colorama>=0.4.6",
    "requests>=2.31.0"
]

# 可选依赖
extras_require = {
    'ai': ['openai>=1.3.0'],
    'dev': [
        'pytest>=7.4.0',
        'pytest-cov>=4.1.0',
        'black>=23.0.0',
        'flake8>=6.0.0',
        'mypy>=1.5.0'
    ],
    'async': ['httpx>=0.25.0']
}

# 所有可选依赖
extras_require['all'] = sum(extras_require.values(), [])

setup(
    name="github-star-summary",
    version="1.0.0",
    author="wangwei",
    author_email="",
    description="GitHub 星标项目分类整理工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AllenHD/star-summary",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "star-summary=cli.main:cli",
            "star-summary-tools=cli.commands:tools",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.md", "*.txt"],
    },
    keywords="github, starred, repositories, classification, markdown",
    project_urls={
        "Bug Reports": "https://github.com/AllenHD/star-summary/issues",
        "Source": "https://github.com/AllenHD/star-summary",
        "Documentation": "https://github.com/AllenHD/star-summary#readme",
    },
)
