import json
from typing import Union, Dict, Optional

from jpype import JInt, JString

from .variables import SYMBOL_CLASS_JSON_PREFIX
from .ByteArray import ByteArray

from ..ffdec.classes import SymbolClassTag


class SymbolClass:
    tag: Optional[SymbolClassTag]

    _symbolTags: Dict[int, Union[bool, str, list, dict]]

    def __init__(self):
        self.tag = None
        self._symbolTags = {}

    def __repr__(self) -> str:
        return str(self._symbolTags)

    def setTag(self, tag: SymbolClassTag):
        self.tag = tag

    def load(self, tag: SymbolClassTag) -> None:
        self.tag = tag

        # Unpack SymbolClass
        for tagNum, tagId in enumerate(self.tag.tags):
            tagData = str(self.tag.names[tagNum])
            jsonData = self._decodeJson(tagData)

            if jsonData is None:
                self._symbolTags[int(tagId)] = tagData

            else:
                self._symbolTags[int(tagId)] = jsonData

    @property
    def loaded(self):
        return self.tag is not None

    def getDict(self, reverseTags=True) -> Dict[int, Union[bool, str, list, dict]]:
        return dict(sorted(self._symbolTags.items(), key=lambda _tagId: _tagId[0], reverse=reverseTags))

    def setDict(self, dict_: Dict[int, Union[bool, str, list, dict]]) -> None:
        self._symbolTags = dict_.copy()

    def _encodeData(self, data: Union[bool, str, dict, list]) -> str:
        if isinstance(data, (bool, dict, list)):
            return f"{SYMBOL_CLASS_JSON_PREFIX}{json.dumps(data)}"

        elif isinstance(data, str):
            return data

        else:
            raise TypeError("Unsupported data type.")

    def _isJsonData(self, data: str) -> bool:
        return data.startswith(SYMBOL_CLASS_JSON_PREFIX)

    def _decodeJson(self, data: str) -> Union[bool, list, dict, None]:
        if self._isJsonData(data):
            try:
                return json.loads(data.replace(SYMBOL_CLASS_JSON_PREFIX, "", 1))
            except json.decoder.JSONDecodeError:
                pass

        return None

    def getNextTagId(self) -> int:
        return max(self._symbolTags.keys()) + 1

    def setTagData(self, tagId: int, tagData: Union[bool, str, list, dict]) -> None:
        self._symbolTags[tagId] = tagData

    def getTagData(self, tagId: int, default=None) -> Union[None, bool, str, list, dict]:
        return self._symbolTags.get(tagId, default)

    def removeTag(self, tagId: int) -> None:
        self._symbolTags.pop(tagId, None)

    def getTagIdByTagData(self, tagData: Union[bool, str, list, dict], default=None) -> Union[None, int]:
        for tagId, tagData_ in self._symbolTags.items():
            if tagData == tagData_:
                return tagId

        return default

    def save(self, reverseTags=True) -> bool:
        if self.tag is not None:
            self.tag.tags.clear()
            self.tag.names.clear()

            for tagId, tagData in self.getDict(reverseTags).items():
                self.tag.tags.add(JInt(tagId))
                self.tag.names.add(JString(self._encodeData(tagData)))

            self.tag.setModified(True)

            return True

        else:
            return False

    def makeByteArray(self, reverseTags=True) -> bytearray:
        if self.tag is not None:
            self.save()
            tagsContent = bytearray(self.tag.getData())

        else:
            tagsContent = ByteArray()
            tagsContent.writeUnsignedShort(len(self._symbolTags))

            for tagId, tagData in self.getDict(reverseTags).items():
                tagsContent.writeUnsignedShort(tagId)
                tagsContent.writeBytes(self._encodeData(tagData).encode())
                tagsContent.writeUnsignedChar(0x00)

        tagID = SymbolClassTag.ID
        tagIDLength = tagID << 6
        tagIDLength += 0x3f

        content = ByteArray()
        content.writeUnsignedShort(tagIDLength)
        content.writeUnsignedInt(len(tagsContent))
        content.writeBytes(tagsContent)

        return content
