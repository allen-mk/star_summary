import unittest
from src.classifier.categories import CategoryManager
from src.classifier.rules import RuleEngine

class TestClassifier(unittest.TestCase):
    def setUp(self):
        self.category_manager = CategoryManager()
        self.rule_engine = RuleEngine(self.category_manager)

    def test_new_graphics_category(self):
        repo_data = {
            'name': 'opengl-renderer',
            'description': 'A real-time rendering engine using OpenGL.',
            'topics': ['computer-graphics', '3d-graphics']
        }
        categories = self.rule_engine.classify(repo_data)
        self.assertIn('graphics', categories)

    def test_new_low_level_category(self):
        repo_data = {
            'name': 'custom-kernel',
            'description': 'A hobby OS kernel written in Assembly and C.',
            'topics': ['systems-programming', 'os-dev']
        }
        categories = self.rule_engine.classify(repo_data)
        self.assertIn('low-level', categories)

    def test_new_awesome_list_category(self):
        repo_data = {
            'name': 'awesome-ai-list',
            'description': 'A curated list of awesome AI resources.',
            'topics': ['awesome-list', 'ai']
        }
        categories = self.rule_engine.classify(repo_data)
        self.assertIn('awesome-list', categories)

    def test_expanded_ai_keywords(self):
        repo_data = {
            'name': 'llm-agent',
            'description': 'An autonomous agent powered by a large language model.',
            'topics': ['ai', 'agent']
        }
        categories = self.rule_engine.classify(repo_data)
        self.assertIn('ai-ml', categories)

    def test_expanded_devops_keywords(self):
        repo_data = {
            'name': 'devcontainer-setup',
            'description': 'A repository with a pre-configured devcontainer for a Python project.',
            'topics': ['devcontainer', 'devops']
        }
        categories = self.rule_engine.classify(repo_data)
        self.assertIn('devops', categories)

if __name__ == '__main__':
    unittest.main()