#!/bin/bash
# 虚拟环境快速设置脚本 (Unix/Linux/macOS)

set -e  # 遇到错误立即退出

echo "🌟 GitHub Star Summary - 虚拟环境快速设置"
echo "=" * 60

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
echo "🐍 检测到 Python 版本: $python_version"

# 检查 Python 版本是否满足要求 (>=3.8)
major_version=$(echo $python_version | cut -d. -f1)
minor_version=$(echo $python_version | cut -d. -f2)

if [[ $major_version -gt 3 ]] || [[ $major_version -eq 3 && $minor_version -ge 8 ]]; then
    echo "✅ Python 版本满足要求"
else
    echo "❌ Python 版本过低，需要 Python 3.8 或更高版本"
    echo "💡 请升级 Python 后再次运行此脚本"
    exit 1
fi

# 运行 Python 设置脚本
echo "🚀 开始设置虚拟环境..."
python3 scripts/setup_env.py

echo ""
echo "🎉 设置完成！请运行以下命令激活虚拟环境："
echo "source activate.sh"
