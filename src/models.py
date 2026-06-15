"""Pydantic models for data validation. Replace with your own."""

from pydantic import BaseModel, Field, field_validator


from datetime import datetime


class SteamArticle(BaseModel):
    id: str = Field(alias="news_id")
    appid: int
    title: str
    url: str | None = None
    author: str | None = "Unknown"
    contents: str | None = "No content available."
    published_at: datetime

    @field_validator("published_at", mode="before")
    @classmethod
    def parse_unix_timestamp(cls, v):
        """Forces Pydantic to reliably parse Unix timestamps, even if they arrive as strings."""
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v)
        if isinstance(v, str) and v.isdigit():
            return datetime.fromtimestamp(int(v))
        return v

    @field_validator("author", mode="before")
    @classmethod
    def empty_author(cls, v):
        return v if v and v.strip() else "Unknown"
