import hashlib


def make_etag(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
