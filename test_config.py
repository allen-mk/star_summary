#!/usr/bin/env python3
"""
配置验证测试脚本

用于验证项目基础架构和配置管理功能。
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_config_loading():
    """测试配置加载功能"""
    print("🔧 测试配置加载...")
    
    try:
        from config.settings import Config
        
        # 测试配置加载
        config = Config()
        print("✅ 配置模块加载成功")
        
        # 测试配置访问
        github_config = config.get('github', {})
        print(f"✅ GitHub配置: {github_config}")
        
        # 测试环境变量
        token = config.github_token
        if token:
            print("✅ GitHub Token已配置")
        else:
            print("⚠️  GitHub Token未配置，请设置GITHUB_TOKEN环境变量")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_github_auth():
    """测试GitHub认证功能"""
    print("\n🔐 测试GitHub认证...")
    
    try:
        from config.settings import Config
        from config.auth import GitHubAuth
        
        config = Config()
        auth = GitHubAuth(config)
        
        if auth.is_authenticated():
            print("✅ GitHub认证成功")
            
            # 测试连接
            if auth.test_connection():
                print("✅ GitHub连接测试通过")
                
                # 显示用户信息
                user_info = auth.get_user_info()
                if 'error' not in user_info:
                    print(f"✅ 用户信息: {user_info['login']}")
                
                # 显示API限制
                rate_limit = auth.get_rate_limit()
                if 'error' not in rate_limit:
                    core = rate_limit['core']
                    print(f"✅ API限制: {core['remaining']}/{core['limit']}")
                
                return True
            else:
                print("❌ GitHub连接测试失败")
                return False
        else:
            print("❌ GitHub认证失败")
            return False
            
    except Exception as e:
        print(f"❌ GitHub认证测试失败: {e}")
        return False

def test_directory_structure():
    """测试目录结构"""
    print("\n📁 检查目录结构...")
    
    required_dirs = [
        'src',
        'src/config',
        'src/github',
        'src/classifier',
        'src/generator',
        'src/cli',
        'src/utils',
        'templates',
        'output'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ (缺失)")
            all_exist = False
    
    return all_exist

def test_required_files():
    """测试必需文件"""
    print("\n📄 检查必需文件...")
    
    required_files = [
        'config.yaml',
        'requirements.txt',
        '.env.example',
        'setup.py',
        'src/__init__.py',
        'src/config/__init__.py',
        'src/config/settings.py',
        'src/config/auth.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (缺失)")
            all_exist = False
    
    return all_exist

def main():
    """主测试函数"""
    print("🚀 GitHub 星标项目分类整理工具 - 基础架构验证")
    print("=" * 60)
    
    tests = [
        ("目录结构", test_directory_structure),
        ("必需文件", test_required_files),
        ("配置加载", test_config_loading),
        ("GitHub认证", test_github_auth)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试出错: {e}")
            results.append((test_name, False))
    
    # 显示测试结果总结
    print("\n" + "=" * 60)
    print("📋 测试结果总结:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！项目基础架构搭建完成。")
        return True
    else:
        print("⚠️  部分测试失败，请检查配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
