import os
import sys
import json

import PyQt5
import PyQt5.QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from core.utils.hash import FileHash
from core.brawlhalla import FindBrawlhalla, BrawlhallaSwfs, BrawlhallaFilesKey
from core.anm.AnmExtractor import AnimationFile, LoadGameFiles, GetObjectsSources, XFLBuilder

WINDOW_NAME = "ANM Exporter"

BRAWLHALLA_PATH = FindBrawlhalla()

CONFIG = {
    "BrawlhallaAirHash": "",
    "FilesKey": 0,
    "BrawlhallaPath": FindBrawlhalla()
}


def SaveConfig():
    with open("config.json", "w", encoding="UTF-8") as cfg:
        cfg.write(json.dumps(CONFIG, indent=4))


def LoadConfig():
    global CONFIG

    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="UTF-8") as cfgFile:
            for key, value in json.loads(cfgFile.read()).items():
                CONFIG[key] = value
    else:
        SaveConfig()


class GameFilesLoader(QObject):
    finished = pyqtSignal()

    def __init__(self, brawlhallaPath: str):
        super().__init__()

    def run(self):
        global CONFIG

        swfs = BrawlhallaSwfs(CONFIG["BrawlhallaPath"])
        bhAirHash = FileHash(swfs["BrawlhallaAir.swf"])

        if bhAirHash == CONFIG["BrawlhallaAirHash"]:
            LoadGameFiles(CONFIG["BrawlhallaPath"], CONFIG["FilesKey"])
        else:
            CONFIG["BrawlhallaAirHash"] = bhAirHash
            CONFIG["FilesKey"] = BrawlhallaFilesKey(swfs["BrawlhallaAir.swf"])
            SaveConfig()

            LoadGameFiles(CONFIG["BrawlhallaPath"], CONFIG["FilesKey"])

        self.finished.emit()


class AnimationTreeItem(QStandardItem):
    packId: int
    animId: int

    def __init__(self, animName: str, packId: int, animId: int):
        super().__init__()
        self.setText(animName)
        self.packId = packId
        self.animId = animId


class AnimationPackTreeItem(QStandardItem):
    packId: int

    def __init__(self, animPackName: str, packId: int):
        super().__init__()
        self.setText(animPackName)


class AnimationFileTreeItem(QStandardItem):
    animPath: str
    animFile: AnimationFile = None

    def __init__(self, animPath: str, fullPath: bool = False):
        super().__init__()
        if fullPath:
            self.setText(animPath)
        else:
            self.setText(os.path.split(animPath)[1])

        self.animPath = animPath

    def load(self):
        if self.animFile is None:
            self.animFile = AnimationFile(self.animPath)
            self._fill()

    def _fill(self):
        if self.animFile is not None:
            for packId in range(self.animFile.packsCount()):
                animPackItem = AnimationPackTreeItem(self.animFile.packName(packId), packId)

                for animId in range(self.animFile.animsCount(packId)):
                    animItem = AnimationTreeItem(self.animFile.animName(packId, animId), packId, animId)
                    animPackItem.appendRow(animItem)

                self.appendRow(animPackItem)


class AnimationsTree(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptDrops(True)
        self.setHeaderHidden(True)
        self.setAlternatingRowColors(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.model = QStandardItemModel(self)
        self.setModel(self.model)

    def addAnimationFile(self, animFilePath: str, fullPath: bool = False):
        animFileItem = AnimationFileTreeItem(animFilePath, fullPath)
        self.model.appendRow(animFileItem)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        pass

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                self.addAnimationFile(url.path().strip("/"), True)
            event.acceptProposedAction()


class MainWindow(QMainWindow):
    brawlhallaPath: str = BRAWLHALLA_PATH


    def __init__(self, parent=None):
        LoadConfig()

        if CONFIG["BrawlhallaPath"] is None:
            raise Exception("Brawlhalla not found!\n\n"
                            "Open 'config.json' and enter your brawlhalla path to 'BrawlhallaPath'")

        super(MainWindow, self).__init__(parent)
        self.setWindowTitle(WINDOW_NAME)
        self.resize(700, 500)

        self.mainFrame = QFrame()
        self.setCentralWidget(self.mainFrame)

        layout = QHBoxLayout(self.mainFrame)
        layout.setContentsMargins(0, 0, 0, 0)

        self.animationsTree = AnimationsTree()
        self.animationsTree.doubleClicked.connect(self.animationsTreeDoubleClick)
        self.animationsTree.customContextMenuRequested.connect(self.animationsTreeMenu)
        layout.addWidget(self.animationsTree)

        # Menu bar
        menuBar = self.menuBar()
        file = menuBar.addMenu("File")
        file.addAction("Open", self.addAnimationFile)

        about = menuBar.addMenu("About")
        about.addAction("About", self.authorDialog)

        #utils = menuBar.addMenu("Utils")
        #utils.addAction("Set brawlhalla path")

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Game files loader
        self.gameFilesLoader = GameFilesLoader(CONFIG["BrawlhallaPath"])
        self.thread = QThread()
        self.thread.started.connect(lambda: self.setWindowTitle(f"{WINDOW_NAME} "
                                                                "(Loading BrawlhallaAir.swf. It will take some time)"))
        self.gameFilesLoader.finished.connect(lambda: self.setWindowTitle(WINDOW_NAME))
        self.thread.started.connect(self.gameFilesLoader.run)
        self.thread.start()

        self.addGameFiles()

    def addGameFiles(self):
        animsPath = os.path.join(CONFIG["BrawlhallaPath"], "anims")
        for anim in os.listdir(animsPath):
            self.animationsTree.addAnimationFile(os.path.join(animsPath, anim))

    def addAnimationFile(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilter("Animation file (*.anm)")

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            if filenames:
                self.animationsTree.addAnimationFile(filenames[0])

    def authorDialog(self):
        author = QDialog()
        author.setWindowTitle("About")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Product: ANM Exporter"))
        layout.addWidget(QLabel("Version: 0.1"))
        layout.addWidget(QLabel("Used: BrawlhallaModloader Core (cut version)"))
        layout.addWidget(QLabel("Author: I_FabrizioG_I"))
        layout.addWidget(QLabel("Discord: I_FabrizioG_I#8111"))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(author.accept)
        layout.addWidget(buttons)

        author.setLayout(layout)

        author.exec_()

    def animationsTreeMenu(self, position):
        menu = QMenu()

        if self.animationsTree.selectedIndexes():
            index = self.animationsTree.selectedIndexes()[0]
            item = index.model().itemFromIndex(index)

            if isinstance(item, AnimationFileTreeItem):
                if item.animFile is None:
                    menu.addAction("Open", lambda: self.animationFileOpen(item))
                else:
                    menu.addAction("Save", lambda: self.animationFileSave(item))

            elif isinstance(item, AnimationTreeItem):
                menu.addAction("Import", lambda: self.animationImport(item))
                menu.addAction("Export", lambda: self.animationExport(item))

        else:
            menu.addAction("Add ANM file", self.addAnimationFile)

        menu.exec_(self.animationsTree.viewport().mapToGlobal(position))

    def animationsTreeDoubleClick(self, index):
        item = index.model().itemFromIndex(index)

        # Open Animation file
        if isinstance(item, AnimationFileTreeItem):
            self.animationFileOpen(item)

    def animationFileOpen(self, animFileTreeItem: AnimationFileTreeItem):
        self.statusBar.showMessage(f"Open ANM file '{animFileTreeItem.animPath}'")
        animFileTreeItem.load()

    def animationFileSave(self, animFileTreeItem: AnimationFileTreeItem):
        path = animFileTreeItem.animFile.save()
        self.statusBar.showMessage(f"Animation file '{path}' saved")

    def animationImport(self, animTreeItem: AnimationTreeItem):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilter("Flash Uncompressed Document (*.xfl)")

        xflFile = None
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            if filenames:
                xflFile = filenames[0]

        if xflFile is None:
            return

        animFileTreeItem: AnimationFileTreeItem = animTreeItem.parent().parent()

        animPath = os.path.split(xflFile)[0]
        xmlName = os.path.split(animPath)[-1]
        xmlPath = os.path.join(animPath, "LIBRARY", f"{xmlName}.xml")

        if animFileTreeItem.animFile.importXML(xmlPath):
            self.statusBar.showMessage(f"Import '{xmlName}.xfl': successful")
        else:
            self.statusBar.showMessage(f"Import '{xmlName}.xfl': failed")

    def animationExport(self, animTreeItem: AnimationTreeItem):
        builder = XFLBuilder(CONFIG["BrawlhallaPath"])

        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)
        dlg.setNameFilter("Save folder")

        saveFolder = None
        if dlg.exec_():
            folders = dlg.selectedFiles()
            if folders:
                saveFolder = folders[0]

        if saveFolder is None:
            return

        animFileTreeItem: AnimationFileTreeItem = animTreeItem.parent().parent()

        try:
            path = builder.exportAnimation(saveFolder, animFileTreeItem.animFile,
                                           animTreeItem.packId, animTreeItem.animId)
            self.statusBar.showMessage(f"Exported to '{os.path.abspath(path)}'")
        except PermissionError:
            self.statusBar.showMessage(f"The file is open in another application!")


def main(*argv):
    app = QApplication(list(argv))
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main(*sys.argv)
