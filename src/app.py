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
        self.windowIcon = str(list(self.preMadePath.glob("window.ico"))[0])
        self.iconbitmap(self.windowIcon)
        # Define variables
        self.selected: Component | Location | None = None
        self.selectedWidget: ctk.CTkFrame | None = None
        self.popup: ctk.CTkToplevel | None = None
        self.locations: dict[int, Location] = {}
        self.components: dict[int, Component] = {}
        self.refreshData()
        # Create the widgets
        self.createWidgets()

    def createWidgets(self) -> None:
        self.tabs = ctk.CTkTabview(self)
        self.tabs.add("Storage")
        self.tabs.add("Parts")
        self.tabs.add("Locations")
        self.tabs.grid(row=0, column=0, sticky="new")
        # Create Stroge tab
        self.storageFrame = ctk.CTkFrame(self.tabs.tab("Storage"))
        self.storageFrame.bind("<Button-1>", self.clearSelected)
        self.storageFrame.pack()
        self.storageFrame.columnconfigure(3, minsize=600, weight=1)
        self.searchComponentLocationEntry = ctk.CTkEntry(self.storageFrame, width=300)
        self.searchComponentLocationEntry.grid(row=0, column=0, sticky="nw")
        self.searchComponentLocationButton = ctk.CTkButton(self.storageFrame, text="", image=self.icons["search"], width=28)
        self.searchComponentLocationButton.grid(row=0, column=1, sticky="nw")
        self.searchComponentLocationValues = ["Components", "Locations", "Quantity", "Price", "Total Price"]
        self.searchComponentLocationVar = ctk.StringVar(value=self.searchComponentLocationValues[1])
        self.searchComponentLocationOptionMenu = ctk.CTkOptionMenu(self.storageFrame, values=self.searchComponentLocationValues, variable=self.searchComponentLocationVar)
        self.searchComponentLocationOptionMenu.grid(row=0, column=2, sticky="nw")
        self.addComponentLocationButton = ctk.CTkButton(self.storageFrame, text="", image=self.icons["plus-circle"], width=28)
        self.addComponentLocationButton.configure(command=lambda: self.createPopup("acl"))
        self.addComponentLocationButton.grid(row=0, column=4, sticky="ne")
        # Create Parts tab
        self.partsFrame = ctk.CTkFrame(self.tabs.tab("Parts"))
        self.partsFrame.bind("<Button-1>", self.clearSelected)
        self.partsFrame.pack()
        self.partsFrame.columnconfigure(3, minsize=600, weight=1)
        self.searchComponentsEntry = ctk.CTkEntry(self.partsFrame, width=300)
        self.searchComponentsEntry.bind("<Return>", self.refreshComponentList)
        self.searchComponentsEntry.grid(row=0, column=0, sticky="nw")
        self.searchComponentsButton = ctk.CTkButton(self.partsFrame, text="", image=self.icons["search"], width=28, command=self.refreshComponentList)
        self.searchComponentsButton.grid(row=0, column=1, sticky="nw")
        self.searchComponentsValues = ["Name", "Price", "Quantity", "Total Price"]
        self.searchComponentsVar = ctk.StringVar(value=self.searchComponentsValues[0])
        self.searchComponentsOptionMenu = ctk.CTkOptionMenu(self.partsFrame, values=self.searchComponentsValues, variable=self.searchComponentsVar, command=self.refreshComponentList)
        self.searchComponentsOptionMenu.grid(row=0, column=2, sticky="nw")
        self.addComponentButton = ctk.CTkButton(self.partsFrame, text="", image=self.icons["plus-circle"], width=28)
        self.addComponentButton.configure(command=lambda: self.createPopup("ac"))
        self.addComponentButton.grid(row=0, column=4, sticky="ne")
        self.componentList = widgets.ComponentList(self.partsFrame, self.icons, list(self.components.values()), self.db, self.searchComponentsVar.get())
        self.componentList.grid(row=1, column=0, columnspan=5, sticky="new")
        # Create Locations tab
        self.locationsFrame = ctk.CTkFrame(self.tabs.tab("Locations"))
        self.locationsFrame.bind("<Button-1>", self.clearSelected)
        self.locationsFrame.pack()
        self.locationsFrame.columnconfigure(3, minsize=600, weight=1)
        self.searchLocationsEntry = ctk.CTkEntry(self.locationsFrame, width=300)
        self.searchLocationsEntry.grid(row=0, column=0, sticky="nw")
        self.searchLocationsButton = ctk.CTkButton(self.locationsFrame, text="", image=self.icons["search"], width=28)
        self.searchLocationsButton.grid(row=0, column=1, sticky="nw")
        self.searchLocationsValues = ["Name", "Parent", "Quantity", "Total Price"]
        self.searchLocationsVar = ctk.StringVar(value=self.searchLocationsValues[0])
        self.searchLocationsOptionMenu = ctk.CTkOptionMenu(self.locationsFrame, values=self.searchLocationsValues, variable=self.searchLocationsVar)
        self.searchLocationsOptionMenu.grid(row=0, column=2, sticky="nw")
        self.addLocationButton = ctk.CTkButton(self.locationsFrame, text="", image=self.icons["plus-circle"], width=28)
        self.addLocationButton.configure(command=lambda: self.createPopup("al"))
        self.addLocationButton.grid(row=0, column=4, sticky="ne")
        self.locationList = widgets.LocationList(self.locationsFrame, self.icons, list(self.locations.values()), self.db, self.searchLocationsVar.get())
        self.locationList.grid(row=1, column=0, columnspan=5, sticky="new")

    def clearSelected(self, *args) -> None:
        msg = "Clearing selected, "
        msg += "None" if self.selected is None else f"Id: {self.selected.id}, Name: {self.selected.name}"
        logger.debug(msg)
        self.selected = None
        if self.selectedWidget:
            self.selectedWidget.destroy()
            self.selectedWidget = None

    def createSelectedWidget(self) -> None:
        if self.selected is None:
            logger.debug("No selected item")
            return
        logger.debug(f"Creating selected widget for {self.selected.id}-{self.selected.name}-{type(self.selected)}")
        if self.selectedWidget:
            self.selectedWidget.destroy()
        if isinstance(self.selected, Component):
            self.selectedWidget = widgets.ComponentInfo(self, self.selected)
        elif isinstance(self.selected, Location):
            self.selectedWidget = widgets.LocationInfo(self, self.selected)
        else:
            logger.error(f"Unknown type: {type(self.selected)}")
            return
        self.selectedWidget.grid(row=0, column=1, sticky="ne", padx=30, pady=20)

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

    def refreshData(self) -> None:
        self.locations.clear()
        self.components.clear()
        for location in self.db.getLocations():
            if not location:
                logger.warning("Location is None")
                continue
            if not location.id:
                logger.warning(f"Location is missing in database: {location.name}")
                continue
            if location.id < 0:
                logger.warning(f"Location is invalid: {location.id}-{location.name}")
                continue
            self.locations[location.id] = location

        for component in self.db.getComponents():
            if not component:
                logger.warning("Component is None")
                continue
            if not component.id:
                logger.warning(f"Component is missing in database: {component.name}")
                continue
            if component.id < 0:
                logger.warning(f"Component is invalid: {component.id}-{component.name}")
                continue
            self.components[component.id] = component

    def refreshComponentList(self, *args) -> None:
        self.refreshData()
        self.componentList.refresh(list(self.components.values()), self.searchComponentsVar.get() ,self.searchComponentsEntry.get())

    def loadIcons(self, paths: Generator[Path, None, None]) -> dict[str, ctk.CTkImage]:
        icons = {}
        for path in paths:
            name = path.stem
            logger.debug(f"Loading icon: {name}")
            image = Image.open(path)
            imageResized = ImageOps.fit(image, (32, 32))
            icons[name] = ctk.CTkImage(imageResized)
        return icons
