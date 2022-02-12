import os

from typing import Union, Optional, List, Dict

from .SymbolClass import SymbolClass
from .MetadataClass import MetadataClass

from .utils import GetTagId, SetTagId

from ..ffdec.classes import *


class SwfClass:
    swfPath:        str
    baseSwf:        Union[None, SWF]

    tagList:        List[Tag]
    symbolClass:    Union[None, SymbolClass]
    metadataClass:  Union[None, MetadataClass]

    _openedSwfs:    Dict[str, 'SwfClass'] = {}

    @classmethod
    def GetSwfClassFromBaseSwf(cls, baseSwf: SWF) -> Union[None, 'SwfClass']:
        for swfClass in cls._openedSwfs.values():
            if swfClass.baseSwf == baseSwf:
                return swfClass

        return None

    @classmethod
    def GetSwfClassFromPath(cls, swfPath: str) -> Union[None, 'SwfClass']:
        return cls._openedSwfs.get(os.path.normpath(swfPath), None)

    def __init__(self, swfPath: str) -> None:
        self.swfPath = os.path.normpath(swfPath)
        self.baseSwf = None

        self.tagList = []
        self.symbolClass = SymbolClass()
        self.metadataClass = MetadataClass()

    def open(self) -> bool:
        if self.swfPath is not None:
            swfFileStream = FileInputStream(self.swfPath)
            self.baseSwf = SWF(swfFileStream, self.swfPath, os.path.split(self.swfPath)[0], True)
            swfFileStream.close()

            self._openedSwfs[self.swfPath] = self

            return True

        else:
            return False

    def load(self) -> bool:
        if self.baseSwf is None:
            return False

        else:
            tagId: int

            for tag in self.baseSwf.getTags():
                tagType = type(tag)
                tagId = -1

                if isinstance(tag, SymbolClassTag):
                    self.symbolClass.load(tag)

                elif tagType == MetadataTag:
                    self.metadataClass.load(tag)

                else:
                    tagId = GetTagId(tag)

                if tagId >= 0:
                    self.tagList.append(tag)

    def save(self) -> bool:
        if self.baseSwf is None:
            return False

        else:
            self.symbolClass.save()
            self.metadataClass.save()

            fileStream = FileOutputStream(self.swfPath)
            self.baseSwf.saveTo(fileStream)
            fileStream.close()

            return True

    def close(self) -> bool:
        if self.baseSwf is None:
            return False

        else:
            self._openedSwfs.pop(self.swfPath)
            self.baseSwf.clearTagSwfs()

            try:
                self.baseSwf.clearAllCache()
            except:
                pass

            self.baseSwf = None
            self.tagList.clear()

            self.metadataClass = None
            self.symbolClass = None

    def addMetadata(self) -> None:
        metadataTag = MetadataTag(self.baseSwf)
        self.baseSwf.addTag(metadataTag)
        self.metadataClass.setTag(metadataTag)

    def getTagsById(self, tagId: int, tagType: Optional[Tag] = None) -> List[Tag]:
        tags = []
        for tag in self.tagList:
            if GetTagId(tag) == tagId and (True if tagType is None else isinstance(tag, tagType)):
                tags.append(tag)

        return tags

    def getTagsByType(self, tagType: Tag) -> List[Tag]:
        tags = []
        for tag in self.tagList:
            if isinstance(tag, tagType):
                tags.append(tag)

        return tags

    def getNextTagId(self) -> int:
        return int(self.baseSwf.getNextCharacterId())

    def getAS3Packs(self):
        return self.baseSwf.getAS3Packs()

    def addTag(self, tag: Tag, tagId: int = -1) -> Tag:
        self.baseSwf.addTag(tag)

        if tagId >= 0:
            SetTagId(tag, tagId)

        self.tagList.append(tag)

        return tag

    def replaceTag(self, oldTag: Tag, newTag: Tag) -> None:
        self.baseSwf.replaceTag(oldTag, newTag)

    # Imports

    # < BinaryData
    def importBinaryData(self, data: bytes, tagId: int) -> DefineBinaryDataTag:
        if tagId is None:
            tagId = self.getNextTagId()

        binaryTag = DefineBinaryDataTag(self.baseSwf)
        binaryTag.binaryData = ByteArrayRange(data, 0, len(data))
        binaryTag.tag = tagId
        binaryTag.setModified(True)

        self.addTag(binaryTag)

        return binaryTag

    def importBinaryFile(self, binaryFilePath: str, tagId: Optional[int] = None):
        with open(binaryFilePath, "rb") as binaryFile:
            binaryTag = self.importBinaryData(binaryFile.read(), tagId)

        return binaryTag

    # < Sound
    def importSoundFile(self, soundPath: str, tagId: Optional[int] = None) -> DefineSoundTag:
        if tagId is None:
            tagId = self.getNextTagId()

        if soundPath.endswith(".mp3"):
            soundFormat = 2
        else:
            soundFormat = 3

        soundTag = DefineSoundTag(self.baseSwf)
        soundTag.setSound(FileInputStream(soundPath), soundFormat)
        soundTag.soundId = tagId
        self.addTag(soundTag)

        return soundTag

    # Exports

    # < BinaryData
    def exportBinaryData(self, tag: Optional[DefineBinaryDataTag] = None,
                         tagId: Optional[int] = None) -> Union[None, bytes]:
        if tag is not None:
            return bytes(tag.getData())[6:]

        elif tagId is not None:
            for element in self.getTagsById(tagId, DefineBinaryDataTag):
                return bytes(element.getData())[6:]

        return None

    def exportBinaryFile(self, binaryFilePath: str, tag: Optional[DefineBinaryDataTag] = None,
                         tagId: Optional[int] = None) -> bool:
        binaryData = self.exportBinaryData(tag, tagId)

        if binaryData is not None:
            with open(binaryFilePath, "wb") as binaryFile:
                binaryFile.write(binaryData)
            return True
        else:
            return False
