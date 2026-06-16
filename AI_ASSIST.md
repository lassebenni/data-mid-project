# AI Assistance Log

Document every time you used an AI tool during this project: what you asked, what it gave you, and what you changed before using it.

This is not about proving you worked hard. It is about building the habit of treating AI output as a first draft, not a final answer.

## Tools used

Claude sonnet 4.6 low
-

## Log

Let me give you a practical cleaning approach for Steam API content fields. The contents field typically contains BBCode, HTML tags, URLs, and other noise. Here's a comprehensive cleaning solution:Here's a comprehensive breakdown of the best regex patterns for cleaning Steam API contents fields, followed by a working pandas pipeline:
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) {
    animation-duration: 0.25s;
    animation-timing-function: cubic-bezier(0.19, 1, 0.22, 1);
  }
VvisualizeVvisualize show_widgetHere's the full cleaning pipeline with every regex explained:
pythonimport re
import html
import pandas as pd

def clean_steam_content(text: str) -> str:
    if not isinstance(text, str):
        return ""

    # ── Step 1: BBCode ──────────────────────────────────────────────
    # [url=http://...] ... [/url]  →  keep inner text
    text = re.sub(r'\[url=[^\]]*\](.*?)\[/url\]', r'\1', text, flags=re.IGNORECASE | re.DOTALL)
    # [img] ... [/img]  →  drop entirely (no useful text)
    text = re.sub(r'\[img\].*?\[/img\]', '', text, flags=re.IGNORECASE | re.DOTALL)
    # [previewyoutube=...][/previewyoutube]  →  drop
    text = re.sub(r'\[previewyoutube[^\]]*\].*?\[/previewyoutube\]', '', text, flags=re.IGNORECASE | re.DOTALL)
    # Any remaining BBCode tag: [b], [/b], [h1], [list], [*], etc.
    text = re.sub(r'\[/?[a-zA-Z0-9]+[^\]]*\]', '', text)

    # ── Step 2: HTML ────────────────────────────────────────────────
    # Self-closing tags like <br />, <img src="..."/>
    text = re.sub(r'<[^>]+/>', ' ', text)
    # Block tags → newline so sentences don't merge
    text = re.sub(r'<(?:p|br|div|li|tr|h[1-6])[^>]*>', '\n', text, flags=re.IGNORECASE)
    # All remaining tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities: &amp; → &, &nbsp; → space, &#39; → '
    text = html.unescape(text)

    # ── Step 3: URLs ────────────────────────────────────────────────
    text = re.sub(r'https?://\S+', '', text)
    # Steam-style bare store links that sometimes lack http
    text = re.sub(r'www\.\S+', '', text)

    # ── Step 4: Special chars & encoding artifacts ──────────────────
    # Windows smart quotes / dashes that slip through as raw bytes
    text = re.sub(r'[\u2018\u2019]', "'", text)   # curly single quotes
    text = re.sub(r'[\u201c\u201d]', '"', text)   # curly double quotes
    text = re.sub(r'\u2014', ' - ', text)          # em-dash
    text = re.sub(r'\u2013', '-', text)            # en-dash
    # Non-printable / control characters (except normal newline)
    text = re.sub(r'[^\x20-\x7E\n]', ' ', text)
    # Repeated punctuation like "!!!!" or "....."
    text = re.sub(r'([!?.,-])\1{2,}', r'\1', text)

    # ── Step 5: Whitespace normalisation ────────────────────────────
    text = re.sub(r'[ \t]+', ' ', text)          # multiple spaces/tabs → one space
    text = re.sub(r'\n{3,}', '\n\n', text)       # 3+ newlines → paragraph break
    text = text.strip()

    return text

create me a table for steam_news (
                    news_id 
                    appid 
                    title 
                    url 
                    author 
                    contents 
                    published_at 
                    ingested_at7:26 AMsqlCREATE TABLE steam_news (
    news_id      TEXT PRIMARY KEY,
    appid        INTEGER NOT NULL,
    title        TEXT,
    url          TEXT,
    author       TEXT,
    contents     TEXT,
    published_at TIMESTAMPTZ,
    ingested_at  TIMESTAMPTZ DEFAULT NOW()
);You said: why is news id text?why is news id text?7:26 AMClaude responded: Steam's gid field (the news ID) comes back as a very large number string like "5208601002087671579" — it exceeds PostgreSQL's BIGINT max, so TEXT is safer.Steam's gid field (the news ID) comes back as a very large number string like "5208601002087671579" — it exceeds PostgreSQL's BIGINT max, so TEXT is safer. But if you've confirmed your IDs fit in 64-bit, you can use BIGINT.

# ── Apply to a DataFrame ────────────────────────────────────────────
df['contents_clean'] = df['contents'].apply(clean_steam_content)

# Optional: drop rows where content is too short after cleaning
df = df[df['contents_clean'].str.len() > 30]

Key decisions explained:
PatternWhy this approach\[url=...\](.*?)\[/url\]Capture group \1 keeps the link label — useful text — while stripping the tag<[^>]+>Matches any HTML tag; [^>]+ avoids catastrophic backtracking vs .*?https?://\S+\S+ grabs the full URL including query strings without needing a long URL regex[^\x20-\x7E\n]Whitelist of printable ASCII; drops junk bytes while preserving newlineshtml.unescape()The stdlib function handles all &entity; and &#NNN; forms correctly — more reliable than regex for this
One gotcha to watch for: Steam content sometimes has {STEAM_CLAN_IMAGE} or {STEAM_CLAN_LOC_IMAGE} template tokens. Add this if you see them:
pythontext = re.sub(r'\{STEAM_CLAN[^}]*\}', '', text)You said: thats too many give me minimal solutinthats too many give me minimal solutin7:12 AMClaude responded: 5 lines, covers 95% of what the Steam contents field throws at you.pythonimport re, html

def clean_steam(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r'\[.*?\]', '', text)           # BBCode tags
    text = re.sub(r'<[^>]+>', '', text)            # HTML tags
    text = html.unescape(text)                     # &amp; &nbsp; etc.
    text = re.sub(r'https?://\S+', '', text)       # URLs
    text = re.sub(r'\s+', ' ', text).strip()       # whitespace
    return text

df['contents_clean'] = df['contents'].apply(clean_steam)
5 lines, covers 95% of what the Steam contents field throws at you.You said: regexesregexes7:13 AMpythonr'\[.*?\]'      # BBCode: [b], [url=...], [img]
r'<[^>]+>'      # HTML tags: <br>, <p>, <strong>
r'https?://\S+' # URLs
r'\s+'          # whitespace (collapse to single space)

### Entry 1

**What I asked:** i am working on a data engineering mid project and i am fetching data from "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/" and contents field include many charactaers whats the best way to clean it using pandas what regex's can clean it best?

**What it gave me:** almost 20 regex to clean using re and html

**What I changed:** i kept going back and forth with it till i reached optimal minimal amount of regex to clean the data without making the code look like a marathon to read, also learned alittle bit about [beautifulsoup, re, html] to be tested later on in the future and used instead of regex but most definetly not on a mid-track projet :)
---


### ENTRY 2

**What I asked:**   create me a table for steam_news (
                    news_id 
                    appid 
                    title 
                    url 
                    author 
                    contents 
                    published_at 
                    ingested_at


**What it gave me:** 

CREATE TABLE steam_news (
    news_id      TEXT PRIMARY KEY,
    appid        INTEGER NOT NULL,
    title        TEXT,
    url          TEXT,
    author       TEXT,
    contents     TEXT,
    published_at TIMESTAMPTZ,
    ingested_at  TIMESTAMPTZ DEFAULT NOW()
);



**What I changed:**why is news id text?
7:26 AM

Steam's gid field (the news ID) comes back as a very large number string like "5208601002087671579" — it exceeds PostgreSQL's BIGINT max, so TEXT is safer. But if you've confirmed your IDs fit in 64-bit, you can use BIGINT.

changed news id to text to be on the safer side and used given table after double checking.

