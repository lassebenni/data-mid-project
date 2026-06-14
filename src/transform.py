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
    df["title"] = df["title"].str.strip().str.title()
    df["url"] = df["url"].str.strip()
    df["published_at"] = pd.to_datetime(df["published_at"], unit="s", errors="coerce")
    df = df.dropna(subset=["news_id", "title"])
    df["author"] = df["author"]
    df["contents"] = df["contents"]
    # 1. Clear HTML tags: <img src="..."> -> eliminated
    df["contents"] = df["contents"].str.replace(r"<[^>]*>", "", regex=True)

    # 2. Clear BBCode tags: [img]...[/img] -> eliminated
    df["contents"] = df["contents"].str.replace(r"\[[^\]]*\]", "", regex=True)

    # 3. Collapse massive whitespace gaps, tabs, and raw newlines (\n) into single spaces
    df["contents"] = df["contents"].str.replace(r"\s+", " ", regex=True).str.strip()

    logger.info("Transformed %d rows successfully", len(df))
    return df
