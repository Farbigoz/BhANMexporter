#import pyximport, os
#if os.path.exists(os.path.join(os.path.split(__file__)[0], "ANMConverter.cp38-win_amd64.pyd")): os.remove(os.path.join(os.path.split(__file__)[0], "ANMConverter.cp38-win_amd64.pyd"))
#pyximport.install(pyximport=True, language_level=3, setup_args={"script_args": ["--cython-cplus"]}, inplace=True)

import os
import time
import enum

from typing import Dict, List

from .ANMConverter import AnimationFile, LoadGameFiles as cLoadGameFiles, GetObjectsSources

from ..base.SwfClass import SwfClass, DefineSpriteTag
from ..base.utils.GetNeededTagsId import GetNeededTagsId
from ..ffdec.classes import XFLConverter, XFLXmlWriter, FLAVersion, HashMap, ArrayList, ReadOnlyTagList, JInt, JString


class LoadGameFilesResult(enum.IntEnum):
    DEPENDENCIES_NOT_FOUND = 0
    GAME_FILES_NOT_FOUND = 1
    INCORRECT_GAME_FILE_DATA = 2
    FILES_LOADED = 3


def LoadGameFiles(brawlhallaPath: str, gameFilesKey: int) -> LoadGameFilesResult:
    return LoadGameFilesResult(cLoadGameFiles(brawlhallaPath, gameFilesKey))


class XFLBuilder:
    backgroundColor: str = "#777777"
    flaVersion: FLAVersion = FLAVersion.CS6
    frameRate: int = 24
    width: int = 1000
    height: int = 800

    replaceObjectsMap = {
        "a_Torso1R": "a_Torso1"
    }

    objectSources: Dict[str, str] = {}

    brawlhallaPath: str

    def __init__(self, brawlhallaPath: str):
        self.brawlhallaPath = brawlhallaPath
        if not os.path.exists(brawlhallaPath):
            raise Exception("Brawlhalla folder is wrong")

        if not self.objectSources:
            for obj, src in GetObjectsSources().items():  # C-type to python
                self.objectSources[obj.decode("UTF-8")] = src.decode("UTF-8")

    def writeContentDOMDocument(self, domDocument: XFLXmlWriter):
        domDocument.writeAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        domDocument.writeAttribute("xmlns", "http://ns.adobe.com/xfl/2008/")
        domDocument.writeAttribute("currentTimeline", "1")
        domDocument.writeAttribute("xflVersion", self.flaVersion.xflVersion())
        domDocument.writeAttribute("creatorInfo", "JPEXS Free Flash Decompiler")
        domDocument.writeAttribute("platform", "Windows")
        domDocument.writeAttribute("versionInfo", "Saved by FFDEc + ANM exporter")
        domDocument.writeAttribute("majorVersion", "14.4.0")
        domDocument.writeAttribute("buildNumber", "")
        domDocument.writeAttribute("nextSceneIdentifier", "2")
        domDocument.writeAttribute("playOptionsPlayLoop", "false")
        domDocument.writeAttribute("playOptionsPlayPages", "false")
        domDocument.writeAttribute("playOptionsPlayFrameActions", "false")
        domDocument.writeAttribute("autoSaveHasPrompted", "true")
        domDocument.writeAttribute("backgroundColor", self.backgroundColor)
        domDocument.writeAttribute("frameRate", str(self.frameRate))
        domDocument.writeAttribute("width", str(self.width))
        domDocument.writeAttribute("height", str(self.height))

    def exportAnimation(self, savePath: str, animFile: AnimationFile, packId: int, animId: int) -> str:
        animName: str = animFile.packName(packId).split("_")[-1] + "_" + animFile.animName(packId, animId)

        neededObjectsMap: Dict[str, List[str]] = {}
        for neededObject in animFile.neededObjects(packId, animId):
            if neededObject in self.replaceObjectsMap:
                neededObject = self.replaceObjectsMap[neededObject]

            if neededObject in self.objectSources:
                source = os.path.join("bones", self.objectSources[neededObject])   # Original animation source
                if source not in neededObjectsMap:
                    neededObjectsMap[source] = [neededObject]
                else:
                    neededObjectsMap[source].append(neededObject)
            else:
                print(f"\t\t\tObject '{neededObject}' not found")

        domDocument = XFLXmlWriter()
        characterVariables = HashMap()
        characterScriptPacks = HashMap()
        nonLibraryShapes = ArrayList()
        files = HashMap()
        datfiles = HashMap()

        domDocument.writeStartElement("DOMDocument")    # Open DOMDocument
        self.writeContentDOMDocument(domDocument)
        domDocument.writeStartElement("symbols")        # Open symbols

        for sourceFile, objectsToExport in neededObjectsMap.items():
            print(f"\t\t\tExport objects from '{sourceFile}'...")

            swf = SwfClass(os.path.join(self.brawlhallaPath, sourceFile))
            swf.open()
            swf.load()

            characters = HashMap()
            characterClasses = HashMap()

            exportTagsId = []
            for objName in objectsToExport:
                objId = swf.symbolClass.getTagIdByTagData(objName)
                obj = swf.getTagsById(objId)
                if obj:
                    exportTagsId += GetNeededTagsId(obj[0])
                    exportTagsId.append(objId)
                    characterClasses[JInt(objId)] = JString(objName)
                else:
                    print(f"\t\t\tObject '{objName}' not found")

            for needTagId in set(exportTagsId):
                obj = swf.getTagsById(needTagId)[0]
                characters[JInt(needTagId)] = obj

                if not isinstance(obj, DefineSpriteTag):
                    characterClasses[JInt(needTagId)] = JString(
                        os.path.split(sourceFile)[-1].replace(".swf", f"_{needTagId}"))

            tags = ReadOnlyTagList(ArrayList(characters.values()))

            XFLConverter().convertSymbols(swf.baseSwf,
                                          characterVariables,
                                          characterClasses,
                                          characterScriptPacks,
                                          nonLibraryShapes,
                                          self.backgroundColor,
                                          tags,
                                          characters,
                                          files,
                                          datfiles,
                                          self.flaVersion,
                                          domDocument)

            swf.close()

        domDocument.writeStartElement("Include")    # Include main animation
        domDocument.writeAttribute("href", f"{animName}.xml")
        domDocument.writeAttribute("loadImmediate", "false")
        domDocument.writeAttribute("lastModified", str(int(time.time())))
        domDocument.writeEndElement()

        domDocument.writeEndElement()                   # Close symbols
        domDocument.writeEndElement()                   # Close DOMDocument

        print(f"\t\t\tBuild '{animName}.xfl'...")
        outDir = os.path.join(savePath, f'{animName}')
        outDirLib = os.path.join(outDir, "LIBRARY")
        if not os.path.exists(outDir):
            os.makedirs(outDir)
        if not os.path.exists(outDirLib):
            os.makedirs(outDirLib)

        with open(os.path.join(outDir, f"{animName}.xfl"), "w") as f:
            f.write("PROXY-CS5")

        with open(os.path.join(outDir, "DOMDocument.xml"), "w") as f:
            f.write(str(domDocument.toString()))

        with open(os.path.join(outDirLib, f"{animName}.xml"), "w") as f:
            f.write(animFile.exportXML(packId, animId))

        for objFileName in files.keys():
            with open(os.path.join(outDirLib, str(objFileName)), "wb") as f:
                f.write(bytes(files[objFileName]))

        return outDir + "\\"


