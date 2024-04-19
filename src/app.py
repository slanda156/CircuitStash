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

        #self.createWidgets()


    def createWidgets(self) -> None:
        widgets.TreeView()
