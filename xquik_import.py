import csv
import io
import json
import re


TEXT_FIELDS = (
    "text",
    "tweetText",
    "Tweet Text",
    "full_text",
    "tweet_text",
    "Tweet_Text",
    "Tweets",
    "content",
    "body",
    "message",
)
CONTAINER_FIELDS = ("data", "items", "results", "tweets", "posts")
NESTED_OBJECT_FIELDS = ("tweet", "post", "item")


class XquikImportError(ValueError):
    pass


def load_xquik_texts(file_or_bytes):
    payload = _read_text(file_or_bytes).strip()
    if not payload:
        raise XquikImportError("Export is empty.")

    rows = _load_rows(payload)
    texts = [_extract_text(row) for row in rows]
    texts = [text for text in texts if text]
    if not texts:
        raise XquikImportError("Export does not contain tweet text fields.")

    return texts


def build_twitter_dataframe(tweets):
    import pandas as pd
    from textblob import TextBlob

    data = pd.DataFrame({"Tweets": tweets})
    data["mentions"] = data["Tweets"].apply(_extract_mentions)
    data["hastags"] = data["Tweets"].apply(_extract_hashtags)
    data["links"] = (
        data["Tweets"].str.extract(r"(https?://\S+)", expand=False).str.strip()
    )
    data["retweets"] = (
        data["Tweets"].str.extract(r"(RT\s+@[A-Za-z0-9_]+)", expand=False).str.strip()
    )
    data["Tweets"] = data["Tweets"].apply(_clean_text)
    data["Subjectivity"] = data["Tweets"].apply(
        lambda text: TextBlob(text).sentiment.subjectivity
    )
    data["Polarity"] = data["Tweets"].apply(
        lambda text: TextBlob(text).sentiment.polarity
    )
    data["Analysis"] = data["Polarity"].apply(_get_analysis)
    return data


def _read_text(file_or_bytes):
    if hasattr(file_or_bytes, "getvalue"):
        value = file_or_bytes.getvalue()
    elif hasattr(file_or_bytes, "read"):
        value = file_or_bytes.read()
    else:
        value = file_or_bytes

    if isinstance(value, bytes):
        try:
            return value.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise XquikImportError("Export must use UTF-8 text encoding.") from error
    if isinstance(value, str):
        return value

    raise XquikImportError("Export must be a text, CSV, JSON, or JSONL file.")


def _load_rows(payload):
    try:
        return _collect_rows(json.loads(payload))
    except json.JSONDecodeError:
        pass

    try:
        rows = [json.loads(line) for line in payload.splitlines() if line.strip()]
    except json.JSONDecodeError:
        rows = []
    if rows:
        return _collect_rows(rows)

    return list(csv.DictReader(io.StringIO(payload)))


def _collect_rows(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for field in CONTAINER_FIELDS:
            nested_value = value.get(field)
            if isinstance(nested_value, list):
                return nested_value
        return [value]

    return []


def _extract_text(row):
    if isinstance(row, str):
        return row.strip()

    if not isinstance(row, dict):
        return ""

    for field in TEXT_FIELDS:
        value = row.get(field)
        if value is not None:
            return str(value).strip()

    for field in NESTED_OBJECT_FIELDS:
        value = row.get(field)
        text = _extract_text(value)
        if text:
            return text

    return ""


def _clean_text(text):
    text = re.sub(r"@[A-Za-z0-9_]+", "", text)
    text = re.sub(r"#", "", text)
    text = re.sub(r"RT\s+", "", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_mentions(text):
    return re.findall(r"@[A-Za-z0-9_]+", text)


def _extract_hashtags(text):
    return re.findall(r"#[A-Za-z0-9_]+", text)


def _get_analysis(score):
    if score < 0:
        return "Negative"
    if score == 0:
        return "Neutral"
    return "Positive"
