"""
AI大模型分类器

使用OpenAI GPT模型进行智能项目分类
"""

import json
import logging
from typing import List, Dict, Any, Optional
import time

from .categories import CategoryManager


logger = logging.getLogger(__name__)


class AIClassifier:
    """
    AI大模型分类器
    
    使用OpenAI GPT模型进行项目分类
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", 
                 category_manager: Optional[CategoryManager] = None):
        """
        初始化AI分类器
        
        Args:
            api_key: OpenAI API密钥
            model: 使用的模型名称
            category_manager: 分类管理器
        """
        self.api_key = api_key
        self.model = model
        self.category_manager = category_manager or CategoryManager()
        
        # 初始化OpenAI客户端
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            logger.info(f"AI分类器初始化完成，使用模型: {model}")
        except ImportError:
            logger.error("未安装openai库，请运行: pip install openai")
            raise
        except Exception as e:
            logger.error(f"OpenAI客户端初始化失败: {e}")
            raise
        
        self.system_prompt = self._build_system_prompt()
        self.request_count = 0
        self.last_request_time = 0
    
    def _build_system_prompt(self) -> str:
        """
        构建系统提示词
        
        Returns:
            系统提示词字符串
        """
        # 获取所有可用分类
        tech_categories = list(self.category_manager.get_categories_by_type('tech_stack').keys())
        purpose_categories = list(self.category_manager.get_categories_by_type('purpose').keys())
        language_categories = list(self.category_manager.get_categories_by_type('language').keys())
        
        return f"""你是一个专业的GitHub项目分类专家。请根据提供的项目信息，将项目分类到以下类别中：

**技术栈分类：**
{', '.join(tech_categories)}

**用途分类：**
{', '.join(purpose_categories)}

**编程语言分类：**
{', '.join(language_categories)}

**分类规则：**
1. 一个项目可以同时属于多个分类
2. 至少选择1个技术栈分类或用途分类
3. 根据项目的主要编程语言选择对应的语言分类
4. 如果项目明显不属于任何已知分类，可以返回空列表

**返回格式：**
请严格按照以下JSON格式返回结果：
{{
  "categories": ["category1", "category2", ...],
  "confidence": 0.95,
  "reasoning": "详细的分类原因和依据"
}}

**注意事项：**
- confidence值应该在0.0-1.0之间，表示分类的置信度
- reasoning应该解释为什么选择这些分类
- 分类时要考虑项目名称、描述、编程语言、topics等所有可用信息"""
    
    def classify_repo(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用AI模型分类单个项目
        
        Args:
            repo_data: 项目数据字典
            
        Returns:
            分类结果字典
        """
        try:
            # 限制请求频率
            self._rate_limit()
            
            # 构建用户提示词
            user_prompt = self._build_user_prompt(repo_data)
            
            # 调用OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # 较低的温度以获得更一致的结果
                max_tokens=500,
                timeout=30
            )
            
            # 解析响应
            response_content = response.choices[0].message.content.strip()
            result = self._parse_ai_response(response_content)
            
            # 验证和清理分类结果
            result['categories'] = self.category_manager.validate_categories(result['categories'])
            result['method'] = 'ai'
            result['model'] = self.model
            
            logger.debug(f"AI分类完成: {repo_data.get('full_name', 'Unknown')} -> {result['categories']}")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"AI响应JSON解析失败: {e}")
            return self._create_fallback_result(f"JSON解析错误: {str(e)}")
        
        except Exception as e:
            logger.error(f"AI分类失败: {e}")
            return self._create_fallback_result(f"AI分类出错: {str(e)}")
    
    def _build_user_prompt(self, repo_data: Dict[str, Any]) -> str:
        """
        构建用户提示词
        
        Args:
            repo_data: 项目数据字典
            
        Returns:
            用户提示词字符串
        """
        # 提取关键信息
        name = repo_data.get('name', 'Unknown')
        full_name = repo_data.get('full_name', 'Unknown')
        description = repo_data.get('description', '无描述')
        language = repo_data.get('language', '未知')
        topics = repo_data.get('topics', [])
        stars = repo_data.get('stargazers_count', 0)
        forks = repo_data.get('forks_count', 0)
        
        # 构建描述性提示词
        prompt = f"""请分类以下GitHub项目：

**项目信息：**
- 项目名称: {name}
- 完整名称: {full_name}
- 编程语言: {language}
- 描述: {description}
- Topics: {', '.join(topics) if topics else '无'}
- 星标数: {stars}
- Fork数: {forks}

请根据以上信息进行分类分析。"""
        
        return prompt
    
    def _parse_ai_response(self, response_content: str) -> Dict[str, Any]:
        """
        解析AI响应内容
        
        Args:
            response_content: AI响应内容
            
        Returns:
            解析后的结果字典
        """
        try:
            # 尝试直接解析JSON
            result = json.loads(response_content)
            
            # 验证必需字段
            if not isinstance(result, dict):
                raise ValueError("响应不是字典格式")
            
            if 'categories' not in result:
                raise ValueError("响应中缺少categories字段")
            
            # 设置默认值
            result.setdefault('confidence', 0.5)
            result.setdefault('reasoning', '无详细说明')
            
            # 确保categories是列表
            if not isinstance(result['categories'], list):
                result['categories'] = [result['categories']] if result['categories'] else []
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            # 尝试从响应中提取可能的JSON
            json_match = self._extract_json_from_text(response_content)
            if json_match:
                try:
                    return json.loads(json_match)
                except:
                    pass
            
            # 如果解析失败，尝试提取关键信息
            logger.warning(f"AI响应解析失败，尝试提取关键信息: {e}")
            return self._extract_categories_from_text(response_content)
    
    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """
        从文本中提取JSON内容
        
        Args:
            text: 包含JSON的文本
            
        Returns:
            提取的JSON字符串
        """
        import re
        
        # 查找JSON模式
        json_patterns = [
            r'\{[^{}]*"categories"[^{}]*\}',
            r'\{.*?\}',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    json.loads(match)
                    return match
                except:
                    continue
        
        return None
    
    def _extract_categories_from_text(self, text: str) -> Dict[str, Any]:
        """
        从文本中提取分类信息
        
        Args:
            text: 响应文本
            
        Returns:
            提取的分类结果
        """
        # 获取所有已知分类
        all_categories = self.category_manager.get_all_categories()
        
        # 在文本中查找分类
        found_categories = []
        text_lower = text.lower()
        
        for category in all_categories:
            if category.lower() in text_lower:
                found_categories.append(category)
        
        return {
            'categories': found_categories if found_categories else ['uncategorized'],
            'confidence': 0.3,
            'reasoning': f"从AI响应文本中提取的分类: {text[:200]}..."
        }
    
    def _create_fallback_result(self, error_msg: str) -> Dict[str, Any]:
        """
        创建回退结果
        
        Args:
            error_msg: 错误信息
            
        Returns:
            回退结果字典
        """
        return {
            'categories': ['uncategorized'],
            'confidence': 0.0,
            'reasoning': error_msg,
            'method': 'ai_fallback',
            'model': self.model
        }
    
    def _rate_limit(self) -> None:
        """
        简单的请求频率限制
        """
        current_time = time.time()
        
        # 确保请求间隔至少0.5秒
        if current_time - self.last_request_time < 0.5:
            sleep_time = 0.5 - (current_time - self.last_request_time)
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def batch_classify(self, repos: List[Dict[str, Any]], batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        批量分类项目
        
        Args:
            repos: 项目数据列表
            batch_size: 批次大小（暂时未使用，每次处理一个）
            
        Returns:
            分类结果列表
        """
        results = []
        
        try:
            from tqdm import tqdm
            repos_iter = tqdm(repos, desc="AI分类项目")
        except ImportError:
            repos_iter = repos
        
        for repo in repos_iter:
            try:
                result = self.classify_repo(repo)
                # 将分类结果合并到原始数据
                repo_with_classification = repo.copy()
                repo_with_classification.update(result)
                results.append(repo_with_classification)
                
            except Exception as e:
                logger.error(f"AI分类项目 {repo.get('full_name', 'Unknown')} 失败: {e}")
                # 添加错误信息
                repo_with_error = repo.copy()
                repo_with_error.update(self._create_fallback_result(str(e)))
                results.append(repo_with_error)
        
        logger.info(f"AI批量分类完成，处理了 {len(results)} 个项目，发送了 {self.request_count} 个API请求")
        
        return results
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        获取使用统计信息
        
        Returns:
            使用统计字典
        """
        return {
            'model': self.model,
            'total_requests': self.request_count,
            'last_request_time': self.last_request_time,
            'average_delay': 0.5  # 固定延迟
        }
    
    def test_connection(self) -> bool:
        """
        测试AI服务连接
        
        Returns:
            连接是否成功
        """
        try:
            # 发送一个简单的测试请求
            test_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "测试连接，请回复'连接成功'"}
                ],
                max_tokens=10,
                timeout=10
            )
            
            response_text = test_response.choices[0].message.content.strip()
            logger.info(f"AI服务连接测试成功: {response_text}")
            return True
            
        except Exception as e:
            logger.error(f"AI服务连接测试失败: {e}")
            return False


def create_ai_classifier(config: Dict[str, Any]) -> Optional[AIClassifier]:
    """
    创建AI分类器的便捷函数
    
    Args:
        config: 配置字典
        
    Returns:
        AI分类器实例，如果配置无效则返回None
    """
    ai_config = config.get('ai_classification', {})
    
    if not ai_config.get('enabled', False):
        logger.info("AI分类未启用")
        return None
    
    # 获取API密钥
    api_key_env = ai_config.get('api_key_env', 'OPENAI_API_KEY')
    
    import os
    api_key = os.getenv(api_key_env)
    
    if not api_key:
        logger.warning(f"未找到OpenAI API密钥，环境变量: {api_key_env}")
        return None
    
    model = ai_config.get('model', 'gpt-3.5-turbo')
    
    try:
        classifier = AIClassifier(api_key, model)
        
        # 测试连接
        if classifier.test_connection():
            logger.info("AI分类器创建成功")
            return classifier
        else:
            logger.error("AI分类器连接测试失败")
            return None
            
    except Exception as e:
        logger.error(f"AI分类器创建失败: {e}")
        return None
