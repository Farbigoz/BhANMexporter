import json
from typing import Union
from .ByteArray import ByteArray
from ..ffdec.classes import MetadataTag


class MetadataClass:
    tag: Union[None, MetadataTag]

    _data: Union[None, bool, str, list, dict]

    def __init__(self):
        self.tag = None
        self._data = None

    def setTag(self, tag: MetadataTag):
        self.tag = tag

    def load(self, tag: MetadataTag) -> None:
        self.tag = tag

        try:
            self._data = json.loads(str(self.tag.xmlMetadata))
        except json.decoder.JSONDecodeError:
            self._data = str(self.tag.xmlMetadata)

    def setData(self, data: Union[None, bool, str, list, dict]) -> None:
        if isinstance(data, (bool, str, list, dict)):
            self._data = data

        else:
            self._data = None

    def getData(self) -> Union[None, bool, str, list, dict]:
        if isinstance(self._data, (bool, list, dict)):
            return self._data.copy()

        elif isinstance(self._data, str):
            return self._data

        else:
            return None

    def save(self) -> bool:
        if self.tag is not None:
            self.tag.xmlMetadata = json.dumps(self._data)
            self.tag.setModified(True)

            return True

        else:
            return False

    def makeByteArray(self) -> bytearray:
        if isinstance(self._data, (bool, list, dict)):
            stringData = json.dumps(self._data)

        elif isinstance(self._data, str):
            stringData = self._data

        else:
            stringData = ""

        tagID = MetadataTag.ID
        tagIDLength = tagID << 6
        tagIDLength += 0x3f

        content = ByteArray()
        content.writeUnsignedShort(tagIDLength)
        content.writeUnsignedInt(len(stringData))
        content.write(stringData.encode("UTF-8"))

        return content
