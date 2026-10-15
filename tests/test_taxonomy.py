from star_summary.taxonomy import Taxonomy


def test_taxonomy_loads_categories_with_names():
    tax = Taxonomy.load_default()
    assert tax.display_name("lang-python") == "Python"
    assert tax.display_name("web-frontend") == "Web前端开发"
    assert tax.is_valid("uncategorized")


def test_taxonomy_rejects_unknown_category():
    tax = Taxonomy.load_default()
    assert not tax.is_valid("web-development")  # README 里的旧名字，不应再有效
    assert not tax.is_valid("fork")


def test_language_mapping():
    tax = Taxonomy.load_default()
    assert tax.language_category("Python") == "lang-python"
    assert tax.language_category("TypeScript") == "lang-typescript"
    assert tax.language_category("Brainfuck") == "lang-other"
