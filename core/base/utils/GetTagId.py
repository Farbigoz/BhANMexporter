from typing import Any

from ...ffdec.classes import *


def GetTagId(tag: Tag) -> int:
    tagType = type(tag)
    tagId = -1

    if tagType in DefineShapeTags:
        tagId = tag.shapeId

    elif tagType == DefineMorphShapeTag:
        tagId = tag.characterId

    elif tagType == DefineSpriteTag:
        tagId = tag.spriteId

    elif tagType == DefineSoundTag:
        tagId = tag.soundId

    elif tagType == DefineTextTag:
        tagId = tag.characterID

    elif tagType == DefineEditTextTag:
        tagId = tag.characterID

    elif tagType == CSMTextSettingsTag:
        tagId = tag.textID

    elif tagType == DefineFontTag:
        tagId = tag.fontId

    elif tagType in DefineFontTags:
        tagId = tag.fontID

    elif tagType == DefineFontNameTag:
        tagId = tag.fontId

    elif tagType == DefineFontAlignZonesTag:
        tagId = tag.fontID

    elif tagType in DefineBitsLosslessTags:
        tagId = tag.characterID

    elif tagType == DefineBinaryDataTag:
        tagId = tag.tag

    elif tagType in PlaceObjectTags:
        tagId = tag.characterId

    tagId = int(tagId)

    if tagId > 0:
        return tagId

    else:
        return -1
