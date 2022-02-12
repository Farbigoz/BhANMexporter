import os
import hashlib


def HashFromBytes(bytes_: bytes) -> str:
    return hashlib.sha256(bytes_).hexdigest()


def RandomHash() -> str:
    return HashFromBytes(os.urandom(2**12))


def FileHash(path: str) -> str:
    with open(path, "rb") as file:
        hash_ = HashFromBytes(file.read())

    return hash_
