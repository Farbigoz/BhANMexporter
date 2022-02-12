from typing import Any

from ...ffdec.classes import *


def SetTagId(tag: Tag, tagId: int) -> Tag:
    tagType = type(tag)

    if tagType in DefineShapeTags:
        tag.shapeId = tagId

    elif tagType == DefineMorphShapeTag:
        tag.characterId = tagId

    elif tagType == DefineSpriteTag:
        tag.spriteId = tagId

    elif tagType == DefineSoundTag:
        tag.soundId = tagId

    elif tagType == DefineTextTag:
        tag.characterID = tagId

    elif tagType == DefineEditTextTag:
        tag.characterID = tagId

    elif tagType == CSMTextSettingsTag:
        tag.textID = tagId

    elif tagType == DefineFontTag:
        tag.fontId = tagId
        tag.characterID = tagId

    elif tagType in DefineFontTags:
        tag.fontID = tagId

    elif tagType == DefineFontNameTag:
        tag.fontId = tagId

    elif tagType == DefineFontAlignZonesTag:
        tag.fontID = tagId

    elif tagType in DefineBitsLosslessTags:
        tag.characterID = tagId

    elif isinstance(tag, PlaceObjectTags):
        tag.characterId = tagId

    # Save new id
    if hasattr(tag, "setModified"):
        tag.setModified(True)

    return tag
