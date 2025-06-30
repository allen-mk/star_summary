#!/bin/bash
set -e

# Docker 入口脚本
echo "🚀 启动 GitHub 星标项目分类工具..."

# 检查必要的环境变量
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ 错误: 未设置 GITHUB_TOKEN 环境变量"
    echo "请设置 GITHUB_TOKEN 环境变量后重试"
    exit 1
fi

# 验证 GitHub Token
echo "🔑 验证 GitHub Token..."
if ! star-summary validate; then
    echo "❌ GitHub Token 验证失败"
    exit 1
fi

# 创建输出目录
mkdir -p /app/output /app/data

# 显示系统状态
echo "📊 系统状态:"
star-summary status

# 执行传入的命令，如果没有传入则执行默认命令
if [ "$#" -eq 0 ]; then
    echo "📝 生成星标项目文档..."
    exec star-summary generate --format both
else
    echo "🔧 执行自定义命令: $@"
    exec "$@"
fi
