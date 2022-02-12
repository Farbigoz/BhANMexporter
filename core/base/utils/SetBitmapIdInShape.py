from typing import Any

from . import GetBitmapIdFromShape


def SetBitmapIdInShape(shape: Any, bitmapId: int) -> bool:
    oldBitmapId = GetBitmapIdFromShape(shape)

    if oldBitmapId >= 0:
        if oldBitmapId != bitmapId:
            shape.shapes.fillStyles.fillStyles[0].bitmapId = bitmapId
            shape.setModified(True)

        return True
    else:
        return False
