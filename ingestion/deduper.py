import hashlib
from pathlib import Path


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    p = Path(path)
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
