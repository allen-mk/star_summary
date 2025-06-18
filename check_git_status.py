#!/usr/bin/env python3
"""
Git 状态检查脚本

检查 .gitignore 文件是否正确忽略了敏感文件和不必要的文件
"""

import os
import subprocess
from pathlib import Path

def run_git_command(command):
    """运行git命令并返回输出"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=Path(__file__).parent
        )
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return f"Error: {e}", 1

def check_gitignore_effectiveness():
    """检查.gitignore文件的有效性"""
    print("🔍 检查 Git 忽略文件状态...")
    print("=" * 50)
    
    # 检查应该被忽略的文件/目录
    should_be_ignored = [
        'venv/',
        '.env',
        'src/config/__pycache__/',
        'src/github_api/__pycache__/',
        '*.pyc',
        '.DS_Store'
    ]
    
    # 检查应该被跟踪的文件
    should_be_tracked = [
        '.gitignore',
        'README.md',
        'config.yaml',
        '.env.example',
        'requirements.txt',
        'setup.py'
    ]
    
    print("📋 应该被忽略的文件/目录:")
    for item in should_be_ignored:
        # 检查文件是否存在
        if '*' in item:  # 通配符文件
            continue
        elif item.endswith('/'):  # 目录
            path = Path(item.rstrip('/'))
        else:  # 文件
            path = Path(item)
        
        if path.exists():
            # 检查是否被git忽略
            output, returncode = run_git_command(f"git check-ignore {item}")
            if returncode == 0:
                print(f"   ✅ {item} - 已忽略")
            else:
                print(f"   ⚠️  {item} - 存在但未被忽略")
        else:
            print(f"   ℹ️  {item} - 不存在")
    
    print("\n📋 应该被跟踪的重要文件:")
    for item in should_be_tracked:
        path = Path(item)
        if path.exists():
            output, returncode = run_git_command(f"git check-ignore {item}")
            if returncode == 0:
                print(f"   ⚠️  {item} - 被意外忽略")
            else:
                print(f"   ✅ {item} - 正常跟踪")
        else:
            print(f"   ❌ {item} - 文件不存在")
    
    # 检查git状态
    print("\n📊 当前 Git 状态:")
    output, returncode = run_git_command("git status --porcelain")
    if returncode == 0:
        if output:
            lines = output.split('\n')
            untracked = [line for line in lines if line.startswith('??')]
            modified = [line for line in lines if line.startswith(' M') or line.startswith('M ')]
            
            print(f"   📄 未跟踪文件: {len(untracked)} 个")
            print(f"   🔄 已修改文件: {len(modified)} 个")
            
            if untracked:
                print("\n   未跟踪的文件:")
                for line in untracked[:10]:  # 只显示前10个
                    print(f"      {line[3:]}")
                if len(untracked) > 10:
                    print(f"      ... 还有 {len(untracked) - 10} 个文件")
        else:
            print("   ✅ 工作目录干净")
    else:
        print(f"   ❌ 获取git状态失败: {output}")
    
    # 检查敏感文件
    print("\n🔐 敏感文件检查:")
    sensitive_files = ['.env', 'config.local.yaml', '*.key', '*.token']
    for pattern in sensitive_files:
        if '*' in pattern:
            continue
        path = Path(pattern)
        if path.exists():
            output, returncode = run_git_command(f"git check-ignore {pattern}")
            if returncode == 0:
                print(f"   ✅ {pattern} - 已安全忽略")
            else:
                print(f"   ⚠️  {pattern} - 存在但未被忽略（安全风险！）")

def main():
    """主函数"""
    print("🔒 GitHub 星标项目分类工具 - Git 忽略文件检查")
    print("=" * 60)
    
    # 检查是否在git仓库中
    if not Path('.git').exists():
        print("❌ 当前目录不是Git仓库")
        return 1
    
    # 检查.gitignore文件是否存在
    if not Path('.gitignore').exists():
        print("❌ .gitignore 文件不存在")
        return 1
    
    check_gitignore_effectiveness()
    
    print("\n" + "=" * 60)
    print("✅ Git 忽略文件检查完成")
    return 0

if __name__ == "__main__":
    exit(main())
