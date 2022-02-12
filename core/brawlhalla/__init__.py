import os
import re
import sys

from typing import Union, Dict

from ..utils.hash import FileHash
from ..ffdec.classes import ArrayList
from ..base.SwfClass import SwfClass


def FindBrawlhalla() -> Union[str, None]:
    brawlhallaPath = None

    if sys.platform in ["win32", "win64"]:
        import winreg

        brawlhallaFolders = []
        steamHomePath = ""

        for reg in ["SOFTWARE\\WOW6432Node\\Valve\\Steam", "SOFTWARE\\Valve\\Steam"]:
            try:
                steamHomePath = winreg.QueryValueEx(
                    winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        reg
                    ),
                    "InstallPath"
                )[0]
                break
            except FileNotFoundError:
                pass

        if steamHomePath:
            with open(os.path.join(os.path.join(steamHomePath, "steamapps"), "libraryfolders.vdf")) as vdf:
                for path in [*re.findall(r'(?:"\d{1,3}"|"path")\t{2}"(.+)"\n', vdf.read()), steamHomePath]:
                    try:
                        folder = os.path.join(path.replace("\\\\", "\\"), "steamapps")
                        if not os.path.exists(folder):
                            continue
                        if "common" in os.listdir(folder) and "Brawlhalla" in os.listdir(
                                os.path.join(folder, "common")):
                            brawlhallaFolders.append(os.path.join(folder, "common", "Brawlhalla"))
                    except:
                        pass

            for folder in brawlhallaFolders:
                if (
                        os.path.exists(folder) and
                        "Brawlhalla.exe" in os.listdir(folder) and
                        "BrawlhallaAir.swf" in os.listdir(folder)
                ):

                    brawlhallaPath = folder

        del brawlhallaFolders
        del steamHomePath

        if brawlhallaPath is None:
            import time
            import psutil

            os.system("start steam://rungameid/291550")

            found = False
            i = 0
            while not found and i < 7:
                time.sleep(1)

                for proc in psutil.process_iter():
                    try:
                        proc_name = proc.name()
                    except psutil.NoSuchProcess:
                        pass
                    else:
                        if proc_name == "Brawlhalla.exe":
                            found = True
                            os.system(f'taskkill /pid {proc.pid}')
                            brawlhallaPath = proc.cwd()
                            break

                i += 1

    elif sys.platform == "darwin":
        pass

    else:
        pass

    return brawlhallaPath


def BrawlhallaSwfs(brawlhallaPath: str) -> Dict[str, str]:
    swfs = {}

    if os.path.exists(brawlhallaPath):
        for path, _, files in os.walk(brawlhallaPath):
            if len(path.replace(brawlhallaPath, "").split("\\")) > 2:
                continue

            for file in files:
                if file.endswith(".swf"):
                    swfs[file] = os.path.join(path, file)

    return swfs


# Files like png, jpg, mp3
def BrawlhallaFiles(brawlhallaPath: str) -> Dict[str, str]:
    files = {}

    if os.path.exists(brawlhallaPath):
        for path, _, folderFiles in os.walk(brawlhallaPath):
            for folderFile in folderFiles:
                if folderFile.endswith(".mp3") or folderFile.endswith(".png") or folderFile.endswith(".jpg"):
                    files[folderFile] = os.path.join(path, folderFile)

    return files


def BrawlhallaAirHash(brawlhallaAirPath: str) -> Union[str, None]:
    if os.path.exists(brawlhallaAirPath) and brawlhallaAirPath.endswith("BrawlhallaAir.swf"):
        return FileHash(brawlhallaAirPath)


def BrawlhallaVersion(brawlhallaAirPath: str) -> Union[str, None]:
    if os.path.exists(brawlhallaAirPath) and brawlhallaAirPath.endswith("BrawlhallaAir.swf"):
        airSwf = SwfClass(brawlhallaAirPath)
        airSwf.open()
        airSwf.load()

        for AS3Pack in airSwf.getAS3Packs():
            methodInfos = ArrayList()
            AS3Pack.getMethodInfos(methodInfos)

            abc = AS3Pack.abc
            for methodInfo in methodInfos:
                bodyIndex = abc.findBodyIndex(methodInfo.getMethodIndex())

                if bodyIndex != -1:
                    body = abc.bodies.get(bodyIndex)
                    pcode = body.getCode().toASMSource(abc)
                    search = re.findall(r'pushstring "(\d\.\d\d|\d\.\d\d\.\d)"', str(pcode))

                    if search:
                        airSwf.close()

                        version: str = search[0]
                        return version

        airSwf.close()

    return None


def BrawlhallaFilesKey(brawlhallaAirPath: str) -> Union[int, None]:
    if os.path.exists(brawlhallaAirPath) and brawlhallaAirPath.endswith("BrawlhallaAir.swf"):
        airSwf = SwfClass(brawlhallaAirPath)
        airSwf.open()
        airSwf.load()

        for AS3Pack in airSwf.getAS3Packs():
            methodInfos = ArrayList()
            AS3Pack.getMethodInfos(methodInfos)

            abc = AS3Pack.abc
            for methodInfo in methodInfos:
                bodyIndex = abc.findBodyIndex(methodInfo.getMethodIndex())

                if bodyIndex != -1:
                    body = abc.bodies.get(bodyIndex)
                    pcode = body.getCode().toASMSource(abc)
                    search = re.findall(r' *getlex QName\(PackageNamespace\("","1"\),"ANE_RawData"\)\r\n'
                                        r' *pushuint (\d*)\r\n'
                                        r' *callpropvoid QName\(PackageNamespace\("","1"\),"Init"\), 1\r\n', str(pcode))

                    if search:
                        airSwf.close()

                        version: int = int(search[0])
                        return version

        airSwf.close()

    return None


#BrawlhallaPath = FindBrawlhalla()
#swfs = BrawlhallaSwfs(BrawlhallaPath)
#print(BrawlhallaPath)
#print(swfs)
#print(BrawlhallaFiles(BrawlhallaPath))
#print(BrawlhallaAirHash(swfs["BrawlhallaAir.swf"]))
#print(BrawlhallaVersion(swfs["BrawlhallaAir.swf"]))
#print(BrawlhallaFilesKey(swfs["BrawlhallaAir.swf"]))
