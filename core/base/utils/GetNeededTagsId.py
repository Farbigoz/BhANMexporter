from ...ffdec.classes import *


def GetNeededTagsId(tag: Tag):
    characters = HashSet()
    tag.getNeededCharactersDeep(characters)
    return sorted(list(characters))
