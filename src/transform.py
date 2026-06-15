from pathlib import Path
import pandas as pd
import logging


logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
JSON_PATH = BASE_DIR / "data" / "raw_steam_news.json"


def transform(articles: list[dict]) -> pd.DataFrame:
    """Load raw JSON data and return two DataFrames: contents and dates."""
    if not articles:
        logger.warning(
            "No articles provided to transform step. Returning empty DataFrame."
        )
        return pd.DataFrame()
    df = pd.DataFrame(articles)
    df = df.drop_duplicates(subset=["news_id"])
    df["title"] = df["title"].str.strip()
    df["url"] = df["url"]
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
    df = df.dropna(subset=["news_id", "title"])
    df["author"] = df["author"]

    df["contents"] = df["contents"].str.replace(
        r"\{STEAM_CLAN_[^\}]*\}/\d+/[a-f0-9]+\.(png|jpg|jpeg|gif)?",
        "",
        regex=True,
        case=False,
    )

    # B. Catch any other lingering curly brace tokens: {EXAMPLE}
    df["contents"] = df["contents"].str.replace(r"\{[^}]*\}", "", regex=True)

    # C. Clear regular HTML tags: <img src="...">
    df["contents"] = df["contents"].str.replace(r"<[^>]*>", "", regex=True)

    # D. Clear regular BBCode tags: [img]...[/img]
    df["contents"] = df["contents"].str.replace(r"\[[^\]]*\]", "", regex=True)

    # E. Collapse double spaces, tabs, and ugly escaped newlines into clean single spaces
    df["contents"] = df["contents"].str.replace(r"\s+", " ", regex=True).str.strip()

    logger.info("Transformed %d rows successfully", len(df))
    return df
