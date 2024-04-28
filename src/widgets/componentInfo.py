from logging import getLogger

import customtkinter as ctk

from ..component import Component
from ..location import Location


logger = getLogger(__name__)


class ComponentInfo(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, component: Component) -> None:
        super().__init__(master, width=132)
        self.component = component
        if self.component.image:
            self.image = ctk.CTkImage(self.component.image, size=(64, 64))
        else:
            self.image = None
        self.args = {"padx": 5, "sticky": "nw"}
        self.createWidgets()

    def createWidgets(self) -> None:
        self.closeButton = ctk.CTkButton(self, text="X", width=28, command=self.master.clearSelected) # type: ignore
        self.closeButton.grid(row=0, column=1, sticky="ne")
        if self.image:
            self.imageLabel = ctk.CTkLabel(self, text="", image=self.image)
            self.imageLabel.grid(row=1, column=0, rowspan=4, sticky="nw")
        self.idLabel = ctk.CTkLabel(self, text=f"ID: {self.component.id}")
        self.idLabel.grid(row=1, column=1, **self.args)
        self.nameLabel = ctk.CTkLabel(self, text=f"Name: {self.component.name}")
        self.nameLabel.grid(row=2, column=1, **self.args)
        self.priceLabel = ctk.CTkLabel(self, text=f"Price: {self.component.price:.2f}€")
        self.priceLabel.grid(row=3, column=1, **self.args)
        self.descriptionTextbox = ctk.CTkTextbox(self, height=64, width=128, wrap="word")
        self.descriptionTextbox.insert("1.0", self.component.description)
        self.descriptionTextbox.configure(state="disabled")
        self.descriptionTextbox.grid(row=4, column=0, columnspan=2, **self.args)
        self.locationLabel = ctk.CTkLabel(self, text="Locations:")
        self.locationLabel.grid(row=5, column=0, columnspan=2, **self.args)
        self.locationFrame = ctk.CTkFrame(self)
        self.locationFrame.grid(row=6, column=0, columnspan=2, **self.args)
        i = 0
        for location, amount in self.component.locations:
            text = f"{location.name} ({amount}) {amount*self.component.price}€"
            locationLabel = ctk.CTkLabel(self.locationFrame, text=text, text_color="blue")
            locationLabel.bind("<Button-1>", lambda e, location=location: self.changeTo(location))
            locationLabel.grid(row=i, column=0, sticky="w", padx=5, pady=5)
            i += 1

    def changeTo(self, location: Location) -> None:
        self.master.selected = location # type: ignore
        self.master.createSelectedWidget() # type: ignore
