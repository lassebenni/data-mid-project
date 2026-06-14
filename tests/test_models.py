"""Example tests for Pydantic models. Replace with your own."""

from datetime import datetime
import pytest
from pydantic import ValidationError
from src.models import SteamArticle


def test_valid_reading():
    """A valid record should be accepted."""
    raw_payload = {
        "news_id": "12345",
        "appid": 570,
        "title": "   dota 2 patch notes   ",
        "url": "  https://steam.com/news/12345  ",
        "published_at": "1718236800",
    }

    article = SteamArticle(**raw_payload)

    assert article.id == "12345"
    assert article.title == "   dota 2 patch notes   "
    assert isinstance(article.published_at, datetime)
    assert article.author == "Unknown"
    assert article.contents == "No content available."
    print("✅ Test 1 Passed: Successful payload parsed and defaulted perfectly!")


def test_validation_failure():
    corrupted_payload = {
        "appid": "not-a-number!!!",
        "title": "Broken Article",
        "published_at": "not-a-date",
    }

    with pytest.raises(ValidationError):
        SteamArticle(**corrupted_payload)
