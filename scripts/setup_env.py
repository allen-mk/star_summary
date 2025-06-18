#!/usr/bin/env python3
"""
虚拟环境自动设置脚本
用于创建和配置 Python 虚拟环境
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def create_virtual_environment():
    """创建虚拟环境"""
    project_root = Path(__file__).parent.parent
    venv_path = project_root / "venv"
    
    print("🚀 开始创建 Python 虚拟环境...")
    print(f"📁 项目根目录: {project_root}")
    print(f"📁 虚拟环境路径: {venv_path}")
    
    # 检查是否已存在虚拟环境
    if venv_path.exists():
        print("⚠️  虚拟环境已存在，是否重新创建？(y/N): ", end="")
        if input().lower() != 'y':
            print("✅ 使用现有虚拟环境")
            return venv_path
        
        print("🗑️  删除现有虚拟环境...")
        import shutil
        shutil.rmtree(venv_path)
    
    # 创建虚拟环境
    print("📦 创建新的虚拟环境...")
    venv.create(venv_path, with_pip=True)
    
    print("✅ 虚拟环境创建成功！")
    return venv_path

def get_activation_script(venv_path):
    """获取激活脚本路径"""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "activate.bat"
    else:
        return venv_path / "bin" / "activate"

def install_dependencies(venv_path):
    """安装项目依赖"""
    project_root = Path(__file__).parent.parent
    requirements_file = project_root / "requirements.txt"
    
    # 获取虚拟环境的 Python 可执行文件
    if sys.platform == "win32":
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    print("📦 安装项目依赖...")
    
    # 升级 pip
    print("⬆️  升级 pip...")
    subprocess.run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], 
                   check=True)
    
    # 安装基础依赖
    if requirements_file.exists():
        print(f"📋 安装 requirements.txt 中的依赖...")
        subprocess.run([str(pip_exe), "install", "-r", str(requirements_file)], 
                       check=True)
    
    # 安装项目本身（开发模式）
    print("🔧 安装项目本身（开发模式）...")
    subprocess.run([str(pip_exe), "install", "-e", ".[dev,ai]"], 
                   cwd=str(project_root), check=True)
    
    print("✅ 依赖安装完成！")

def create_activation_helpers(venv_path):
    """创建激活辅助脚本"""
    project_root = Path(__file__).parent.parent
    
    # 创建 Unix/Linux/macOS 激活脚本
    activate_sh = project_root / "activate.sh"
    with open(activate_sh, 'w') as f:
        f.write(f"""#!/bin/bash
# 激活虚拟环境
echo "🚀 激活 GitHub Star Summary 虚拟环境..."
source {venv_path}/bin/activate
echo "✅ 虚拟环境已激活！"
echo "💡 使用 'deactivate' 命令退出虚拟环境"
echo "💡 使用 'star-summary --help' 查看工具帮助"
""")
    
    # 设置执行权限
    os.chmod(activate_sh, 0o755)
    
    # 创建 Windows 激活脚本
    activate_bat = project_root / "activate.bat"
    with open(activate_bat, 'w') as f:
        f.write(f"""@echo off
REM 激活虚拟环境
echo 🚀 激活 GitHub Star Summary 虚拟环境...
call {venv_path}\\Scripts\\activate.bat
echo ✅ 虚拟环境已激活！
echo 💡 使用 'deactivate' 命令退出虚拟环境
echo 💡 使用 'star-summary --help' 查看工具帮助
""")
    
    print("✅ 激活脚本创建完成！")
    return activate_sh, activate_bat

def create_env_file(project_root):
    """创建环境变量文件"""
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("📝 创建 .env 文件...")
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ .env 文件已创建，请编辑并填入您的 API 密钥")
    
def main():
    """主函数"""
    print("=" * 60)
    print("🌟 GitHub Star Summary - 虚拟环境设置")
    print("=" * 60)
    
    try:
        # 创建虚拟环境
        venv_path = create_virtual_environment()
        
        # 安装依赖
        install_dependencies(venv_path)
        
        # 创建激活辅助脚本
        activate_sh, activate_bat = create_activation_helpers(venv_path)
        
        # 创建环境变量文件
        project_root = Path(__file__).parent.parent
        create_env_file(project_root)
        
        print("\n" + "=" * 60)
        print("🎉 环境设置完成！")
        print("=" * 60)
        print("\n📋 下一步操作：")
        print("1. 编辑 .env 文件，填入您的 GitHub Token 和 OpenAI API Key")
        print("2. 激活虚拟环境：")
        if sys.platform == "win32":
            print(f"   Windows: .\\activate.bat 或 {venv_path}\\Scripts\\activate.bat")
        else:
            print(f"   Unix/Linux/macOS: source activate.sh 或 source {venv_path}/bin/activate")
        print("3. 运行工具: star-summary --help")
        print("\n💡 提示：每次使用前需要先激活虚拟环境")
        
    except Exception as e:
        print(f"❌ 设置失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
