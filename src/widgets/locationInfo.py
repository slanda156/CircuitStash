from logging import getLogger

import customtkinter as ctk

from ..location import Location


logger = getLogger(__name__)


class LocationInfo(ctk.CTkFrame):
    def __init__(self, master, location: Location) -> None:
        super().__init__(master)
        self.location = location
        self.args = {"padx": 5, "pady": 2, "sticky": "nw"}
        self.createWidgets()

    def createWidgets(self) -> None:
        self.closeButton = ctk.CTkButton(self, text="X", width=28, command=self.master.clearSelected) # type: ignore
        self.closeButton.grid(row=0, column=0, sticky="ne")
        self.idLabel = ctk.CTkLabel(self, text=f"ID: {self.location.id}")
        self.idLabel.grid(row=0, column=0, **self.args)
        self.parentLabel = ctk.CTkLabel(self, text=f"Parent: {self.location.parentID}")
        self.parentLabel.grid(row=1, column=0, **self.args)
        self.nameLabel = ctk.CTkLabel(self, text=f"Name: {self.location.name}|{self.location.shortName}")
        self.nameLabel.grid(row=2, column=0, **self.args)
        self.descriptionTextbox = ctk.CTkTextbox(self, height=64, width=128, wrap="word")
        self.descriptionTextbox.insert("1.0", self.location.description)
        self.descriptionTextbox.configure(state="disabled")
        self.descriptionTextbox.grid(row=3, column=0, **self.args)
