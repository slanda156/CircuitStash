from logging import getLogger
import customtkinter as ctk
from pathlib import Path

from src import widgets
from src.database import Database


logger = getLogger(__name__)


class App(ctk.CTk):
    def init(self) -> None:
        self.title("Circuit Stash")
        self.state("zoomed")
        self.minsize(200, 200)
        self.configure(background="white")

        self.dataPath = Path.cwd() / Path("data")
        self.dataPath.mkdir(exist_ok=True)

        self.docsPath = self.dataPath / Path("docs")
        self.docsPath.mkdir(exist_ok=True)

        self.imgPath = self.dataPath / Path("img")
        self.imgPath.mkdir(exist_ok=True)

        self.preMadePath = Path.cwd() / Path("src/img")
        if not self.preMadePath.exists():
            raise FileNotFoundError("Pre-made image path does not exist")

        self.db = Database()
        self.db.connect()
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
