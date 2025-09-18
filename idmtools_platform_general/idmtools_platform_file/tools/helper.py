import re
import unicodedata

def safe(s: str, maxlen: int = 30) -> str:
    """
    Sanitize a string to be safe for folder names.
    Replaces unsafe characters, trims, and truncates.
    """
    # Normalize unicode to ASCII (e.g. é → e)
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')

    # Lowercase and replace spaces with underscores
    s = s.lower().replace(" ", "_")

    # Replace any remaining invalid characters with underscores
    s = re.sub(r'[^a-z0-9_.-]', '_', s)

    # Collapse repeated underscores or dashes
    s = re.sub(r'[_-]{2,}', '_', s)

    # Strip leading/trailing undesired characters
    s = s.strip("_.-")

    # Truncate to maxlen
    return s[:maxlen]
