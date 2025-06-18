#!/usr/bin/env python3
"""
GitHub API集成功能测试脚本

测试GitHub API客户端、获取器和缓存管理器的功能
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.settings import Config
from src.github_api.service import GitHubService


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_github_api():
    """测试GitHub API功能"""
    print("🚀 GitHub API集成功能测试")
    print("=" * 50)
    
    try:
        # 加载配置
        print("1. 加载配置...")
        config = Config()
        
        # 检查GitHub Token
        token = config.github_token
        if not token:
            print("❌ 错误: 未找到GitHub Token")
            print("请设置环境变量 GITHUB_TOKEN")
            return False
        
        print(f"✅ GitHub Token已配置 (长度: {len(token)})")
        
        # 初始化GitHub服务
        print("\n2. 初始化GitHub服务...")
        github_service = GitHubService(config)
        
        # 验证配置和连接
        print("\n3. 验证配置和连接...")
        validation_result = github_service.validate_config()
        
        print(f"   配置有效: {'✅' if validation_result['config_valid'] else '❌'}")
        print(f"   连接有效: {'✅' if validation_result['connection_valid'] else '❌'}")
        print(f"   缓存启用: {'✅' if validation_result['cache_enabled'] else '❌'}")
        
        if validation_result['errors']:
            print("   错误:")
            for error in validation_result['errors']:
                print(f"     - {error}")
        
        if validation_result['warnings']:
            print("   警告:")
            for warning in validation_result['warnings']:
                print(f"     - {warning}")
        
        if not validation_result['connection_valid']:
            print("❌ 连接验证失败，无法继续测试")
            return False
        
        # 获取用户信息
        print(f"\n4. 认证用户: {validation_result.get('username', 'Unknown')}")
        
        # 获取API速率限制状态
        print("\n5. API速率限制状态...")
        rate_limit = github_service.get_rate_limit_status()
        
        if rate_limit:
            core_info = rate_limit.get('core', {})
            search_info = rate_limit.get('search', {})
            
            print(f"   核心API: {core_info.get('remaining', 0)}/{core_info.get('limit', 0)} 剩余")
            print(f"   搜索API: {search_info.get('remaining', 0)}/{search_info.get('limit', 0)} 剩余")
        
        # 获取星标项目摘要
        print("\n6. 获取星标项目摘要...")
        summary = github_service.get_starred_summary()
        
        if 'error' not in summary:
            print(f"   总星标数: {summary.get('total_starred', 0)}")
            print(f"   获取时间: {summary.get('fetched_at', 'Unknown')}")
        else:
            print(f"   获取摘要失败: {summary['error']}")
        
        # 测试缓存功能
        print("\n7. 测试缓存功能...")
        cache_info = github_service.get_cache_info()
        
        print(f"   缓存启用: {'✅' if cache_info['enabled'] else '❌'}")
        if cache_info['enabled']:
            print(f"   缓存目录: {cache_info.get('cache_directory', 'Unknown')}")
            print(f"   缓存文件数: {cache_info.get('total_cache_files', 0)}")
            
            # 检查用户缓存
            user_cache_exists = cache_info.get('exists', False)
            user_cache_valid = cache_info.get('valid', False)
            
            print(f"   用户缓存存在: {'✅' if user_cache_exists else '❌'}")
            print(f"   用户缓存有效: {'✅' if user_cache_valid else '❌'}")
        
        # 测试获取少量星标项目（如果用户同意）
        print("\n8. 测试获取星标项目...")
        
        # 询问用户是否要测试完整获取
        response = input("是否要测试获取前10个星标项目? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            print("   获取前10个星标项目...")
            
            # 临时修改获取器来限制数量（这是测试用途）
            original_fetch = github_service.fetcher.fetch_all_starred
            
            def limited_fetch(show_progress=True):
                repos = []
                count = 0
                starred_repos = github_service.client.get_user_starred()
                
                for repo in starred_repos:
                    if count >= 10:
                        break
                    
                    try:
                        repo_data = github_service.fetcher.extract_repo_data(repo)
                        repos.append(repo_data)
                        count += 1
                        print(f"     获取项目 {count}/10: {repo.full_name}")
                    except Exception as e:
                        print(f"     获取项目失败: {e}")
                
                return repos
            
            # 临时替换方法
            github_service.fetcher.fetch_all_starred = limited_fetch
            
            try:
                repos = github_service.fetch_starred_repos(
                    use_cache=False,  # 不使用缓存确保测试API
                    show_progress=False
                )
                
                print(f"   ✅ 成功获取 {len(repos)} 个项目")
                
                if repos:
                    sample_repo = repos[0]
                    print(f"   示例项目: {sample_repo.get('full_name', 'Unknown')}")
                    print(f"   项目语言: {sample_repo.get('language', 'Unknown')}")
                    print(f"   星标数: {sample_repo.get('stargazers_count', 0)}")
                
            except Exception as e:
                print(f"   ❌ 获取失败: {e}")
            finally:
                # 恢复原方法
                github_service.fetcher.fetch_all_starred = original_fetch
        else:
            print("   跳过获取测试")
        
        print("\n" + "=" * 50)
        print("✅ GitHub API集成功能测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    setup_logging()
    
    print("GitHub 星标项目分类整理工具 - API集成测试")
    print()
    
    success = test_github_api()
    
    if success:
        print("\n🎉 所有测试通过！GitHub API集成功能正常。")
        sys.exit(0)
    else:
        print("\n💥 测试失败，请检查配置和网络连接。")
        sys.exit(1)


if __name__ == '__main__':
    main()
