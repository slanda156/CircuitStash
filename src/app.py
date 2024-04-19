from logging import getLogger
import customtkinter as ctk

from src import widgets
from src.database import Database
from src.component import Component


logger = getLogger(__name__)


class App(ctk.CTk):
    def init(self) -> None:
        self.title("Circuit Stash")
        self.state("zoomed")
        self.minsize(200, 200)
        self.configure(background="white")

        self.db = Database()
        self.db.connect()

        c = Component("Test4", description="This is a test component", price=1.0, imagePath="test.png", datasheetPath="test.pdf")
        self.db.createComponent(c)

        #self.createWidgets()


    def createWidgets(self) -> None:
        widgets.TreeView()
