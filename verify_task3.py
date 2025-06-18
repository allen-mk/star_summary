#!/usr/bin/env python3
"""
任务3验证脚本：智能项目分类系统

验证分类系统的功能是否正常工作
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.config.settings import Config
from src.classifier.classifier import ProjectClassifier
from src.classifier.rules import RuleEngine
from src.classifier.categories import CategoryManager
from src.classifier.hybrid_classifier import HybridClassifier


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_repo_data() -> List[Dict[str, Any]]:
    """创建测试用的仓库数据"""
    return [
        {
            "id": 1,
            "name": "react",
            "full_name": "facebook/react",
            "description": "A declarative, efficient, and flexible JavaScript library for building user interfaces.",
            "language": "JavaScript",
            "topics": ["javascript", "react", "frontend", "ui", "library"],
            "stargazers_count": 200000,
            "forks_count": 41000,
            "html_url": "https://github.com/facebook/react",
            "homepage": "https://reactjs.org/",
            "created_at": "2013-05-24T16:15:54Z",
            "updated_at": "2023-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "name": "tensorflow",
            "full_name": "tensorflow/tensorflow",
            "description": "An Open Source Machine Learning Framework for Everyone",
            "language": "Python",
            "topics": ["machine-learning", "deep-learning", "ai", "python", "tensorflow"],
            "stargazers_count": 170000,
            "forks_count": 86000,
            "html_url": "https://github.com/tensorflow/tensorflow",
            "homepage": "https://www.tensorflow.org/",
            "created_at": "2015-11-07T01:19:20Z",
            "updated_at": "2023-01-01T00:00:00Z"
        },
        {
            "id": 3,
            "name": "awesome-python",
            "full_name": "vinta/awesome-python",
            "description": "A curated list of awesome Python frameworks, libraries, software and resources",
            "language": "Python",
            "topics": ["awesome", "python", "list", "resources"],
            "stargazers_count": 150000,
            "forks_count": 23000,
            "html_url": "https://github.com/vinta/awesome-python",
            "homepage": "",
            "created_at": "2014-06-27T21:00:06Z",
            "updated_at": "2023-01-01T00:00:00Z"
        },
        {
            "id": 4,
            "name": "docker",
            "full_name": "moby/moby",
            "description": "Moby Project - a collaborative project for the container ecosystem",
            "language": "Go",
            "topics": ["docker", "containers", "moby", "go"],
            "stargazers_count": 65000,
            "forks_count": 18000,
            "html_url": "https://github.com/moby/moby",
            "homepage": "https://mobyproject.org/",
            "created_at": "2013-01-18T18:10:57Z",
            "updated_at": "2023-01-01T00:00:00Z"
        },
        {
            "id": 5,
            "name": "unknown-project",
            "full_name": "test/unknown-project",
            "description": "A test project with no clear category",
            "language": "Text",
            "topics": [],
            "stargazers_count": 10,
            "forks_count": 2,
            "html_url": "https://github.com/test/unknown-project",
            "homepage": "",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
    ]


def test_category_manager():
    """测试分类管理器"""
    print("\\n" + "="*50)
    print("测试分类管理器")
    print("="*50)
    
    try:
        category_manager = CategoryManager()
        
        # 测试获取所有分类
        categories = category_manager.get_all_categories()
        print(f"✓ 加载分类数量: {len(categories)}")
        
        # 测试验证分类
        valid_categories = ["web-frontend", "ai-ml", "lang-python"]
        invalid_categories = ["invalid-category", "non-existent"]
        
        for cat in valid_categories:
            assert category_manager.is_valid_category(cat), f"有效分类验证失败: {cat}"
        print(f"✓ 有效分类验证通过: {valid_categories}")
        
        for cat in invalid_categories:
            assert not category_manager.is_valid_category(cat), f"无效分类验证失败: {cat}"
        print(f"✓ 无效分类验证通过: {invalid_categories}")
        
        # 测试关键词匹配
        tech_keywords = category_manager.tech_stack_keywords
        assert len(tech_keywords) > 0, "技术栈关键词为空"
        print(f"✓ 技术栈关键词数量: {len(tech_keywords)}")
        
        print("✓ 分类管理器测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 分类管理器测试失败: {e}")
        return False


def test_rule_engine():
    """测试规则引擎"""
    print("\\n" + "="*50)
    print("测试规则引擎")
    print("="*50)
    
    try:
        rule_engine = RuleEngine()
        rule_engine.setup_default_rules()
        
        print(f"✓ 加载规则数量: {len(rule_engine.rules)}")
        
        # 测试分类
        test_repos = create_test_repo_data()
        
        for repo in test_repos[:3]:  # 测试前3个项目
            categories = rule_engine.classify(repo)
            print(f"✓ {repo['name']}: {categories}")
            assert isinstance(categories, list), "分类结果应该是列表"
            assert len(categories) > 0, "分类结果不应该为空"
        
        print("✓ 规则引擎测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 规则引擎测试失败: {e}")
        return False


def test_ai_classifier():
    """测试AI分类器（如果配置了API密钥）"""
    print("\\n" + "="*50)
    print("测试AI分类器")
    print("="*50)
    
    try:
        # 检查是否有OpenAI API密钥
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("⚠ 未配置OPENAI_API_KEY，跳过AI分类器测试")
            return True
        
        from src.classifier.ai_classifier import AIClassifier
        
        category_manager = CategoryManager()
        ai_classifier = AIClassifier(
            api_key=api_key,
            model="gpt-3.5-turbo",
            category_manager=category_manager
        )
        
        print("✓ AI分类器初始化成功")
        
        # 测试单个项目分类（仅测试第一个项目以节省API调用）
        test_repo = create_test_repo_data()[0]  # React项目
        result = ai_classifier.classify_repo(test_repo)
        
        print(f"✓ AI分类结果: {result}")
        
        # 验证返回格式
        required_fields = ['categories', 'confidence', 'reasoning', 'method']
        for field in required_fields:
            assert field in result, f"AI分类结果缺少字段: {field}"
        
        assert isinstance(result['categories'], list), "categories应该是列表"
        assert isinstance(result['confidence'], (int, float)), "confidence应该是数值"
        assert 0 <= result['confidence'] <= 1, "confidence应该在0-1之间"
        
        print("✓ AI分类器测试通过")
        return True
        
    except ImportError:
        print("⚠ openai库未安装，跳过AI分类器测试")
        return True
    except Exception as e:
        print(f"✗ AI分类器测试失败: {e}")
        return False


def test_hybrid_classifier():
    """测试混合分类器"""
    print("\\n" + "="*50)
    print("测试混合分类器")
    print("="*50)
    
    try:
        # 加载配置
        config_manager = Config()
        config = config_manager.config
        
        hybrid_classifier = HybridClassifier(config)
        print("✓ 混合分类器初始化成功")
        
        # 测试分类
        test_repos = create_test_repo_data()
        
        for repo in test_repos[:3]:  # 测试前3个项目
            result = hybrid_classifier.classify_repo(repo)
            print(f"✓ {repo['name']}: {result['categories']} (方法: {result['method']})")
            
            # 验证返回格式
            required_fields = ['categories', 'method', 'confidence', 'reasoning']
            for field in required_fields:
                assert field in result, f"混合分类结果缺少字段: {field}"
        
        print("✓ 混合分类器测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 混合分类器测试失败: {e}")
        return False


def test_project_classifier():
    """测试主分类器"""
    print("\\n" + "="*50)
    print("测试主分类器")
    print("="*50)
    
    try:
        # 加载配置
        config_manager = Config()
        config = config_manager.config
        
        # 测试不同的分类方法
        methods = ['rules', 'hybrid']
        
        # 如果有OpenAI API密钥，也测试AI分类
        if os.getenv('OPENAI_API_KEY'):
            methods.append('ai')
        
        test_repos = create_test_repo_data()
        
        for method in methods:
            print(f"\\n--- 测试分类方法: {method} ---")
            
            # 更新配置
            test_config = config.copy()
            test_config['classification'] = {'method': method}
            
            classifier = ProjectClassifier(test_config)
            print(f"✓ {method}分类器初始化成功")
            
            # 测试单个项目分类
            repo = test_repos[0]  # React项目
            result = classifier.classify_repo(repo)
            print(f"✓ {repo['name']}: {result['categories']} (置信度: {result['confidence']:.2f})")
            
            # 验证分类结果
            assert classifier.validate_classification_result(result), f"{method}分类结果验证失败"
            
            # 测试批量分类（仅测试2个项目以节省时间）
            batch_results = classifier.classify_batch(test_repos[:2], show_progress=False)
            print(f"✓ 批量分类完成，处理了 {len(batch_results)} 个项目")
            
            # 获取统计信息
            stats = classifier.get_classification_stats(batch_results)
            print(f"✓ 统计信息: {stats['total_repos']} 个项目, 方法: {stats.get('method', method)}")
        
        print("✓ 主分类器测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 主分类器测试失败: {e}")
        return False


def test_batch_classification():
    """测试批量分类功能"""
    print("\\n" + "="*50)
    print("测试批量分类功能")
    print("="*50)
    
    try:
        config_manager = Config()
        config = config_manager.config
        classifier = ProjectClassifier(config)
        
        test_repos = create_test_repo_data()
        
        # 测试批量分类
        results = classifier.classify_batch(test_repos, show_progress=True)
        
        print(f"✓ 批量分类完成，处理了 {len(results)} 个项目")
        
        # 验证结果
        for result in results:
            assert 'repo' in result, "批量分类结果应包含repo字段"
            assert 'classification' in result, "批量分类结果应包含classification字段"
            
            classification = result['classification']
            assert classifier.validate_classification_result(classification), "分类结果验证失败"
        
        # 获取统计信息
        stats = classifier.get_classification_stats(results)
        print(f"✓ 统计信息: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        
        print("✓ 批量分类功能测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 批量分类功能测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("开始验证任务3：智能项目分类系统")
    print("="*60)
    
    test_results = []
    
    # 运行所有测试
    tests = [
        ("分类管理器", test_category_manager),
        ("规则引擎", test_rule_engine),
        ("AI分类器", test_ai_classifier),
        ("混合分类器", test_hybrid_classifier),
        ("主分类器", test_project_classifier),
        ("批量分类功能", test_batch_classification),
    ]
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            test_results.append((test_name, success))
        except Exception as e:
            logger.error(f"测试 {test_name} 时出现异常: {e}")
            test_results.append((test_name, False))
    
    # 汇总结果
    print("\\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！任务3智能项目分类系统验证成功！")
        return True
    else:
        print(f"⚠ {total - passed} 项测试失败，请检查相关功能")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
