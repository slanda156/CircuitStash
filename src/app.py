from logging import getLogger
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageOps

from src import widgets
from src.database import Database

from src.component import Component
from src.location import Location
from typing import Generator


logger = getLogger(__name__)


class App(ctk.CTk):
    def init(self) -> None:
        # Set the window
        self.title("Circuit Stash")
        self.state("zoomed")
        self.minsize(640, 480)
        self.configure(background="white")
        # Create diffrent paths
        self.dataPath = Path.cwd() / Path("data")
        self.dataPath.mkdir(exist_ok=True)
        self.docsPath = self.dataPath / Path("docs")
        self.docsPath.mkdir(exist_ok=True)
        self.imgPath = self.dataPath / Path("img")
        self.imgPath.mkdir(exist_ok=True)
        self.preMadePath = Path.cwd() / Path("src/img")
        if not self.preMadePath.exists():
            raise FileNotFoundError("Pre-made image path does not exist")
        # Create the database
        self.db = Database()
        self.db.connect()
        # Load Icons for window
        self.icons = self.loadIcons(self.preMadePath.glob("*.ico"))
        self.popup: ctk.CTkToplevel | None = None

    def createWidgets(self) -> None:
    def createPopup(self, type: str, id: int=-1) -> None:
        if self.popup:
            logger.warning("Popup already exists")
            self.destroyPopup()
        if type == "acl":
            self.popup = widgets.AddComponentLocation(self.db, self)
        elif type == "ac":
            self.popup = widgets.AddComponent(self.db, self)
        elif type == "al":
            self.popup = widgets.AddLocation(self.db, self)
        elif type == "ccl":
            self.popup = widgets.ChangeComponentLocation(id, self.db, self)
        elif type == "cc":
            self.popup = widgets.ChangeComponent(id, self.db, self)
        elif type == "cl":
            self.popup = widgets.ChangeLocation(id, self.db, self)
        else:
            logger.error(f"Unknown popup type: {type}")
            return
        self.popup.destroyFunc = self.destroyPopup
        self.popup.protocol("WM_DELETE_WINDOW", self.destroyPopup)
        self.popup.transient(self)
        self.popup.wait_visibility()
        self.popup.grab_set()
        self.popup.wait_window()

    def destroyPopup(self) -> None:
        if self.popup:
            logger.debug(f"Destroying popup, \"{self.popup.title()}\"")
            self.popup.grab_release()
            self.popup.destroy()
            self.popup = None

    def loadIcons(self, paths: Generator[Path, None, None]) -> dict[str, ctk.CTkImage]:
        icons = {}
        for path in paths:
            name = path.stem
            logger.debug(f"Loading icon: {name}")
            image = Image.open(path)
            imageResized = ImageOps.fit(image, (32, 32))
            icons[name] = ctk.CTkImage(imageResized)
        return icons
