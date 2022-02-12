from typing import Union

from ...ffdec.classes import *


def GetBitmapIdFromShape(shape: Union[DefineShapeTags]) -> int:
    if isinstance(shape, DefineShapeTags):
        shape.getShapes()

        if (
                hasattr(shape, "shapes") and
                hasattr(shape.shapes, "fillStyles") and
                hasattr(shape.shapes.fillStyles, "fillStyles") and
                len(shape.shapes.fillStyles.fillStyles) == 1 and
                shape.shapes.fillStyles.fillStyles[0].fillStyleType == 64
        ):
            return int(shape.shapes.fillStyles.fillStyles[0].bitmapId)

    return -1
