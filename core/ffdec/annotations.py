from typing import List, Optional, Generic, TypeVar, Any
if False:
    from .classes import HashSet


T = TypeVar("T")


# JAVA CLASSES ---------------------------------------------------------------------------------------------------------
class ArrayList(list, Generic[T]):
    def add(self, arg: Any):
        ...

    def get(self, i: int):
        return self[i]


class FileInputStream:
    def __init__(self, filePath: str) -> None:
        ...

    def close(self) -> None:
        ...


class FileOutputStream:
    def __init__(self, filePath: str) -> None:
        ...

    def close(self) -> None:
        ...


# ffdec CLASSES -------------------

# > Helpers
class ByteArrayRange:
    def __init__(self, array: bytes, pos: int, length: int) -> None:
        ...


class CodeFormatting:
    pass


class HighlightedTextWriter:
    def __init__(self, formatting: CodeFormatting, hilight: bool):
        ...


# > Configs
class Configuration:
    @classmethod
    def getCodeFormatting(cls) -> CodeFormatting:
        ...


# > Scripts
class AVM2Code:
    @classmethod
    def toASMSource(cls, abc: "ABC") -> str:
        ...


class MethodBody:
    def getCode(self) -> AVM2Code:
        ...


class MethodId:
    def getMethodIndex(self) -> int:
        ...


class ABC:
    bodies: ArrayList[MethodBody]

    def findBodyIndex(self, methodInfo: int) -> int:
        ...


class ScriptPack:
    abc: ABC

    def getMethodInfos(self, methodInfos: ArrayList[MethodId]) -> None:
        ...


# > Tags
class Tag:
    ID: int
    NAME: str

    def __init__(self, swf: "SWF", id: int = 0, name: str = "", data: bytes = b"") -> None:
        ...

    def setModified(self, modified: bool) -> None:
        ...

    def cloneTag(self) -> 'Tag':
        ...

    def getData(self) -> bytes:
        ...

    def getNeededCharactersDeep(self, hashSet: 'HashSet') -> List['Tag']:
        ...


class SymbolClassTag(Tag):
    ID = 76
    NAME = "SymbolClass"

    tags: ArrayList[int]
    names: ArrayList[str]


class MetadataTag(Tag):
    ID = 77
    NAME = "Metadata"

    xmlMetadata: str


class DefineBinaryDataTag(Tag):
    tag: int
    binaryData: ByteArrayRange


class DefineSoundTag(Tag):
    soundId: int

    def setSound(self, fileInputStream: FileInputStream, soundFormat: int) -> None:
        ...


# ffdec MAIN CLASS


class SWF:
    def __init__(self, fileInputStream: FileInputStream, filePath: str, fileTitle: str,
                 parallelRead: bool = False) -> None:
        ...

    def addTag(self, tag: Tag):
        ...

    def replaceTag(self, oldTag: Tag, newTag: Tag) -> None:
        ...

    def getTags(self) -> List[Tag]:
        ...

    def clearTagSwfs(self) -> None:
        ...

    def clearAllCache(self) -> None:
        ...

    def getFile(self) -> Optional[str]:
        ...

    def getFileTitle(self) -> Optional[str]:
        ...

    def getNextCharacterId(self) -> int:
        ...

    def getAS3Packs(self) -> List[ScriptPack]:
        ...

    def saveTo(self, fileOutputStream: FileOutputStream) -> None:
        ...

