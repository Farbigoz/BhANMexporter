import os
from typing import Union

from .cpchecksum import CPCheckSum


def CheckSum(content: bytes, length: int = 4) -> str:
    return CPCheckSum(content, len(content), length)[::-1].hex()


def RandomCheckSum(length: int) -> str:
    return CheckSum(os.urandom(64), length)


def FileCheckSum(filePath: str, length: int) -> Union[str, None]:
    if os.path.exists(filePath):
        with open(filePath, "rb") as f:
            checksum = CheckSum(f.read(), length)

        return checksum

    return None
