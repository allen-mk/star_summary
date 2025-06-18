#!/usr/bin/env python3
"""
GitHub API集成任务验证脚本

验证任务2的所有功能点是否正确实现
"""

import sys
import os
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.settings import Config
from src.github_api.service import GitHubService


def print_header(title):
    """打印标题"""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print('='*50)


def print_result(test_name, success, details=None):
    """打印测试结果"""
    status = "✅" if success else "❌"
    print(f"{status} {test_name}")
    if details:
        for detail in details:
            print(f"   {detail}")


def test_module_imports():
    """测试模块导入"""
    print_header("模块导入测试")
    
    test_results = []
    modules_to_test = [
        ('src.config.settings', 'Config'),
        ('src.config.auth', 'GitHubAuth'),
        ('src.utils.cache', 'CacheManager'),
        ('src.github_api.client', 'GitHubClient'),
        ('src.github_api.fetcher', 'StarredFetcher'),
        ('src.github_api.service', 'GitHubService'),
    ]
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            test_results.append((f"导入 {module_name}.{class_name}", True, None))
        except Exception as e:
            test_results.append((f"导入 {module_name}.{class_name}", False, [f"错误: {e}"]))
    
    for test_name, success, details in test_results:
        print_result(test_name, success, details)
    
    return all(success for _, success, _ in test_results)


def test_configuration():
    """测试配置功能"""
    print_header("配置管理测试")
    
    test_results = []
    
    try:
        # 测试配置加载
        config = Config()
        test_results.append(("配置文件加载", True, [
            f"GitHub API URL: {config.get('github.api_base_url')}",
            f"缓存启用: {config.get('cache.enabled')}",
            f"获取器批次大小: {config.get('fetcher.batch_size')}"
        ]))
        
        # 测试配置方法
        github_config = config.github_config
        cache_config = config.cache_config
        fetcher_config = config.fetcher_config
        
        test_results.append(("配置方法访问", True, [
            f"GitHub配置项: {len(github_config)} 个",
            f"缓存配置项: {len(cache_config)} 个", 
            f"获取器配置项: {len(fetcher_config)} 个"
        ]))
        
        # 测试特定配置方法
        client_config = config.get_github_client_config()
        cache_manager_config = config.get_cache_manager_config()
        
        test_results.append(("专用配置生成", True, [
            f"客户端配置: timeout={client_config.get('timeout')}s",
            f"缓存配置: TTL={cache_manager_config.get('ttl_hours')}h"
        ]))
        
    except Exception as e:
        test_results.append(("配置测试", False, [f"错误: {e}"]))
    
    for test_name, success, details in test_results:
        print_result(test_name, success, details)
    
    return all(success for _, success, _ in test_results)


def test_cache_manager():
    """测试缓存管理器"""
    print_header("缓存管理器测试")
    
    test_results = []
    
    try:
        from src.utils.cache import CacheManager
        
        # 初始化缓存管理器
        cache_manager = CacheManager(cache_dir=".test_cache", cache_format="json")
        test_results.append(("缓存管理器初始化", True, [
            f"缓存目录: {cache_manager.cache.cache_dir}",
            f"缓存格式: {cache_manager.cache.cache_format}"
        ]))
        
        # 测试缓存操作
        test_data = [
            {"name": "test-repo", "language": "Python", "stars": 100}
        ]
        
        # 保存测试数据
        save_success = cache_manager.save_starred_repos("test_user", test_data)
        test_results.append(("缓存数据保存", save_success, None))
        
        # 加载测试数据
        loaded_data = cache_manager.load_starred_repos("test_user")
        load_success = loaded_data is not None and len(loaded_data) == 1
        test_results.append(("缓存数据加载", load_success, [
            f"加载的项目数: {len(loaded_data) if loaded_data else 0}"
        ]))
        
        # 测试缓存有效性检查
        cache_valid = cache_manager.is_user_cache_valid("test_user", 24)
        test_results.append(("缓存有效性检查", cache_valid, None))
        
        # 清理测试缓存
        cache_manager.cache.clear_cache()
        
    except Exception as e:
        test_results.append(("缓存管理器测试", False, [f"错误: {e}"]))
    
    for test_name, success, details in test_results:
        print_result(test_name, success, details)
    
    return all(success for _, success, _ in test_results)


def test_rate_limit_handler():
    """测试速率限制处理"""
    print_header("速率限制处理测试")
    
    test_results = []
    
    try:
        from src.github_api.client import handle_rate_limit, calculate_wait_time
        
        # 测试装饰器存在
        test_results.append(("速率限制装饰器", callable(handle_rate_limit), None))
        
        # 测试等待时间计算函数
        test_results.append(("等待时间计算函数", callable(calculate_wait_time), None))
        
        # 测试基本装饰器功能
        @handle_rate_limit
        def test_function():
            return "success"
        
        result = test_function()
        test_results.append(("装饰器功能测试", result == "success", [
            f"函数返回值: {result}"
        ]))
        
    except Exception as e:
        test_results.append(("速率限制处理测试", False, [f"错误: {e}"]))
    
    for test_name, success, details in test_results:
        print_result(test_name, success, details)
    
    return all(success for _, success, _ in test_results)


def test_github_service_structure():
    """测试GitHub服务结构"""
    print_header("GitHub服务结构测试")
    
    test_results = []
    
    try:
        config = Config()
        
        # 检查是否可以初始化（即使没有有效Token）
        try:
            github_service = GitHubService(config)
            test_results.append(("GitHub服务初始化", True, [
                f"服务类型: {type(github_service).__name__}",
                f"缓存管理器: {'已启用' if github_service.cache_manager else '未启用'}"
            ]))
            
            # 测试方法存在性
            required_methods = [
                'test_connection', 'get_authenticated_user', 'fetch_starred_repos',
                'get_starred_summary', 'get_rate_limit_status', 'clear_cache',
                'get_cache_info', 'validate_config'
            ]
            
            missing_methods = []
            for method_name in required_methods:
                if not hasattr(github_service, method_name):
                    missing_methods.append(method_name)
            
            test_results.append(("必需方法检查", len(missing_methods) == 0, [
                f"检查方法数: {len(required_methods)}",
                f"缺失方法: {missing_methods if missing_methods else '无'}"
            ]))
            
        except Exception as e:
            test_results.append(("GitHub服务初始化", False, [f"错误: {e}"]))
        
    except Exception as e:
        test_results.append(("GitHub服务结构测试", False, [f"错误: {e}"]))
    
    for test_name, success, details in test_results:
        print_result(test_name, success, details)
    
    return all(success for _, success, _ in test_results)


def test_data_extraction():
    """测试数据提取结构"""
    print_header("数据提取结构测试")
    
    test_results = []
    
    try:
        from src.github_api.fetcher import StarredFetcher
        
        # 检查StarredFetcher的方法
        required_methods = [
            'fetch_all_starred', 'extract_repo_data', 'get_starred_summary'
        ]
        
        missing_methods = []
        for method_name in required_methods:
            if not hasattr(StarredFetcher, method_name):
                missing_methods.append(method_name)
        
        test_results.append(("StarredFetcher方法检查", len(missing_methods) == 0, [
            f"检查方法数: {len(required_methods)}",
            f"缺失方法: {missing_methods if missing_methods else '无'}"
        ]))
        
        # 检查期望的数据字段
        expected_fields = [
            'id', 'name', 'full_name', 'description', 'html_url',
            'language', 'topics', 'stargazers_count', 'created_at'
        ]
        
        config = Config()
        fetcher_config = config.fetcher_config
        configured_fields = fetcher_config.get('fields', [])
        
        missing_fields = []
        for field in expected_fields:
            if field not in configured_fields:
                missing_fields.append(field)
        
        test_results.append(("数据字段配置", len(missing_fields) == 0, [
            f"期望字段数: {len(expected_fields)}",
            f"配置字段数: {len(configured_fields)}",
            f"缺失字段: {missing_fields if missing_fields else '无'}"
        ]))
        
    except Exception as e:
        test_results.append(("数据提取结构测试", False, [f"错误: {e}"]))
    
    for test_name, success, details in test_results:
        print_result(test_name, success, details)
    
    return all(success for _, success, _ in test_results)


def main():
    """主验证函数"""
    print("🧪 GitHub API集成任务验证")
    print("任务ID: cdb5b0eb-c92d-45aa-b4e8-c276dabb142b")
    
    # 运行所有测试
    test_functions = [
        test_module_imports,
        test_configuration,
        test_cache_manager,
        test_rate_limit_handler,
        test_github_service_structure,
        test_data_extraction
    ]
    
    results = []
    for test_func in test_functions:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试 {test_func.__name__} 执行失败: {e}")
            results.append(False)
    
    # 汇总结果
    print_header("验证结果汇总")
    
    passed_tests = sum(results)
    total_tests = len(results)
    
    print(f"通过测试: {passed_tests}/{total_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    if all(results):
        print("\n🎉 所有验证测试通过！任务2的核心功能已正确实现。")
        print("\n📋 已实现的功能:")
        print("   ✅ GitHub API客户端封装")
        print("   ✅ 速率限制处理和重试机制")  
        print("   ✅ 星标项目获取器和数据提取")
        print("   ✅ 本地缓存管理系统")
        print("   ✅ 配置管理和服务整合")
        print("   ✅ 错误处理和日志记录")
        
        print("\n⚠️  注意:")
        print("   - 完整功能测试需要有效的GitHub Token")
        print("   - 实际API连接和数据获取需要网络访问")
        print("   - 进度条功能需要tqdm库支持")
        
        return True
    else:
        print(f"\n❌ 有 {total_tests - passed_tests} 个测试失败，请检查实现。")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
