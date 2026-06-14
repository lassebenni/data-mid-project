import logging
import time
import requests

logger = logging.getLogger(__name__)

API_URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"


def fetch_with_retry(
    url: str, params: dict, max_retries: int = 3, timeout: int = 10
) -> dict:
    """Fetch url with exponential backoff on transient errors.

    Retry on: ConnectionError, Timeout, 5xx status codes.
    Fail immediately on: 4xx status codes.
    Log each retry attempt with the error and delay.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code < 500:
                logger.error(
                    f"Client error {e.response.status_code}. Failing immediately."
                )
                raise

            error_msg = f"Server error {e.response.status_code}"
            error_type = error_msg

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            error_type = type(e).__name__

        if attempt == max_retries - 1:
            logger.error(
                f"Max retries reached. Final attempt failed with {error_type}."
            )
            raise

        wait_time = 2**attempt
        logger.warning(
            f"Attempt {attempt + 1} failed ({error_type}). Retrying in {wait_time}s..."
        )
        time.sleep(wait_time)

    raise RuntimeError("unreachable")


def fetch_api_records(appid: int) -> list[dict]:
    """Fetch news articles from Steam API and return flat dicts.

    Returns a list of dicts with keys: appid, title, url, author, contents.
    Returns [] if the API returns no data (do not raise an exception).
    """
    params = {
        "appid": appid,
        "count": 20,
        "maxlength": 0,
    }

    try:
        data = fetch_with_retry(API_URL, params=params)
    except Exception as e:
        logger.error(f"Failed to fetch data from API: {e}")
        return []

    articles = data.get("appnews", {}).get("newsitems", [])
    if not articles:
        logger.warning("API response structure was missing expected articles data.")
        return []

    return [
        {
            "appid": article.get("appid"),
            "news_id": str(
                article.get("gid")
            ),  # Converted to string to prevent data loss
            "title": article.get("title"),
            "url": article.get("url"),
            "author": article.get("author"),
            "contents": article.get("contents"),
            "published_at": article.get("date"),
        }
        for article in articles
    ]
