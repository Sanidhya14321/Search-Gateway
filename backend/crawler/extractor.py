import re

try:
    from bs4 import BeautifulSoup
except Exception:  # pragma: no cover - fallback when bs4 is unavailable
    BeautifulSoup = None


def extract_clean_text(raw_html: str) -> str:
    if not raw_html:
        return ""

    if BeautifulSoup is None:
        text = re.sub(r"<script[\s\S]*?</script>", " ", raw_html, flags=re.IGNORECASE)
        text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<nav[\s\S]*?</nav>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<footer[\s\S]*?</footer>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<header[\s\S]*?</header>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    soup = BeautifulSoup(raw_html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript", "svg", "iframe"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()
