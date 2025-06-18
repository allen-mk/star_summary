#!/usr/bin/env python3
"""
测试虚拟环境和配置加载功能

这个脚本验证：
1. 虚拟环境是否正确激活
2. 配置文件是否能正确加载
3. GitHub认证是否工作正常
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_virtual_environment():
    """测试虚拟环境"""
    print("🔍 检查虚拟环境...")
    
    # 检查是否在虚拟环境中
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print("✅ 正在使用虚拟环境")
        print(f"   Python路径: {sys.executable}")
        print(f"   虚拟环境路径: {sys.prefix}")
    else:
        print("⚠️  未检测到虚拟环境，建议使用虚拟环境")
        print(f"   当前Python路径: {sys.executable}")
    
    return in_venv

def test_config_loading():
    """测试配置加载"""
    print("\n🔍 测试配置加载...")
    
    try:
        from config.settings import Config
        config = Config()
        
        print("✅ 配置加载成功")
        
        # 测试基本配置获取
        github_token_env = config.get('github.token_env', 'GITHUB_TOKEN')
        print(f"   GitHub Token环境变量名: {github_token_env}")
        
        output_format = config.get('output.format', 'markdown')
        print(f"   输出格式: {output_format}")
        
        # 测试输出路径配置
        output_config = config.get_output_config()
        if output_config:
            print("✅ 输出配置获取成功")
            main_readme_path = config.get_output_path('main_readme')
            print(f"   主README路径: {main_readme_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_github_auth():
    """测试GitHub认证"""
    print("\n🔍 测试GitHub认证...")
    
    try:
        from config.settings import Config
        from config.auth import GitHubAuth
        
        config = Config()
        auth = GitHubAuth(config)
        
        if auth.client is None:
            print("⚠️  GitHub客户端创建失败，请检查GITHUB_TOKEN环境变量")
            return False
        
        # 测试API连接
        if auth.client:
            user_info = auth.get_user_info()
            if 'error' not in user_info:
                print(f"✅ GitHub认证成功")
                print(f"   用户名: {user_info.get('login', 'Unknown')}")
                print(f"   显示名: {user_info.get('name', 'Unknown')}")
                return True
            else:
                print(f"❌ GitHub认证失败: {user_info['error']}")
                return False
        else:
            print("❌ GitHub客户端未初始化")
            return False
            
    except Exception as e:
        print(f"❌ GitHub认证测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖包"""
    print("\n🔍 测试依赖包...")
    
    required_packages = [
        'github', 'yaml', 'dotenv', 'click', 
        'jinja2', 'tqdm', 'colorama', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (缺失)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺失的依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包都已安装")
    return True

def main():
    """主测试函数"""
    print("🚀 GitHub 星标项目分类工具 - 环境测试")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        ("虚拟环境", test_virtual_environment),
        ("依赖包", test_dependencies),
        ("配置加载", test_config_loading),
        ("GitHub认证", test_github_auth),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试出现异常: {e}")
            results.append((test_name, False))
    
    # 输出总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！环境配置正确。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查环境配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
