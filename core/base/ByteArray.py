import struct
from typing import Union


class ByteArray(bytearray):
    def __init__(self, *args):
        super().__init__(*args)

        self.offset = 0

    # Base w\r methods
    def writeBytes(self, data: Union[bytes, bytearray]) -> None:
        for _elem in data:
            self.append(_elem)

    def readBytes(self, length: int) -> bytearray:
        bytes_ = self[self.offset:self.offset + length]
        self.offset += length

        return bytes_

    # Write methods
    def writeUnsignedInt(self, data: int):
        self += struct.pack("<I", data)

    def writeUnsignedShort(self, data: int):
        self += struct.pack("<H", data)

    def writeUnsignedChar(self, data: int):
        self += struct.pack("<B", data)

    # Read methods
    def readUnsignedInt(self):
        return struct.unpack('<I', self.readBytes(4))[0]

    def readShort(self):
        return struct.unpack('<h', self.readBytes(2))[0]

    def readUnsignedShort(self):
        return struct.unpack('<H', self.readBytes(2))[0]

    def readDouble(self):
        return struct.unpack('<d', self.readBytes(8))[0]

    def readBool(self):
        return struct.unpack('?', self.readBytes(1))[0]

    def readUTF(self):
        length = self.readUnsignedShort()
        return self.readBytes(length).decode("UTF-8")
