import json
from pathlib import Path

from star_summary.models import Classification, Repo

FIXTURE = Path(__file__).parent / "fixtures" / "starred_sample.json"


def load_sample():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_repo_from_dict_keeps_core_fields():
    raw = load_sample()[0]
    repo = Repo.from_dict(raw)
    assert repo.full_name == raw["full_name"]
    assert repo.language == raw["language"]
    assert repo.stargazers_count == raw["stargazers_count"]
    assert repo.topics == raw["topics"]


def test_classification_is_one_category():
    category = Classification(category="编程工具")
    assert category.category == "编程工具"


def test_classified_repo_is_flat_and_serialisable():
    raw = load_sample()[0]
    repo = Repo.from_dict(raw)
    classified = repo.with_classification(Classification(category="编程工具"))
    data = classified.to_dict()
    assert data["full_name"] == raw["full_name"]
    assert data["category"] == "编程工具"
