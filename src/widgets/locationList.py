from logging import getLogger

import customtkinter as ctk

from src.location import Location
from src.widgets import ChangeLocation

from src.database import Database
from src.component import Component

logger = getLogger(__name__)


class LocationToSort(Location):
    def __init__(self, location: Location, components: list[Component]) -> None:
        super().__init__(
                            id=location.id,
                            name=location.name,
                            shortName=location.shortName,
                            description=location.description,
                        )
        self.components = components
        self.quantity = sum([quantity for component in self.components for locationId, quantity in component.locations if locationId == location.id])
        self.totalPrice = sum([component.price * quantity for component in self.components for locationId, quantity in component.locations if locationId == location.id])


class LocationWidget(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkScrollableFrame, location: LocationToSort, icons: dict[str, ctk.CTkImage], db: Database) -> None:
        super().__init__(parent)
        self.location = location
        self.icons = icons
        self.db = db
        self.popup: ChangeLocation | None = None
        self.createWidgets()

    def createWidgets(self) -> None:
        self.columnconfigure(0, minsize=200)
        self.columnconfigure(1, minsize=100)
        self.columnconfigure(2, minsize=100)
        self.columnconfigure(3, minsize=80)
        self.columnconfigure(4, minsize=250, weight=1)
        args = {"sticky": "nw", "padx": 5, "pady": 5}
        self.nameLabel = ctk.CTkLabel(self, text=self.location.name)
        self.nameLabel.grid(row=0, column=0, **args)
        self.shortNameLabel = ctk.CTkLabel(self, text=self.location.shortName)
        self.shortNameLabel.grid(row=0, column=1, **args)
        self.totalPriceLabel = ctk.CTkLabel(self, text=f"{self.location.totalPrice:.2f}€")
        self.totalPriceLabel.grid(row=0, column=2, **args)
        self.quantityLabel = ctk.CTkLabel(self, text=f"{self.location.quantity}")
        self.quantityLabel.grid(row=0, column=3, **args)
        self.descriptionTextbox = ctk.CTkTextbox(self, width=250, height=50)
        self.descriptionTextbox.insert("1.0", self.location.description)
        self.descriptionTextbox.grid(row=0, column=4, **args)
        self.changeButon = ctk.CTkButton(self, text="", image=self.icons["edit-pencil"], width=28, command=self.change)
        self.changeButon.grid(row=0, column=5, **args)

    def change(self) -> None:
        logger.info(f"Changing location {self.location.name}")
        self.popup = ChangeLocation(self.location, self.db, self)


class LocationList(ctk.CTkScrollableFrame):
    def __init__(self, parent: ctk.CTkBaseClass, icons: dict[str, ctk.CTkImage], locations: list[Location], db: Database, sorting: str, search: str="") -> None:
        super().__init__(parent)
        self.icons = icons
        self.db = db
        self.sortedComponent: list[LocationToSort] = []
        self.locationWidgets: list[LocationWidget] = []
        self.refresh(locations, sorting, search)

    def refresh(self, locations: list[Location], sorting: str, search: str="") -> None:
        self.locations: list[LocationToSort] = []
        for location in locations:
            if location.id is not None:
                self.locations.append(LocationToSort(location, self.db.getComponentsInLocation(location.id)))
            else:
                self.locations.append(LocationToSort(location, []))
        self.sorting = sorting
        self.search = search if search else None
        self.sortLocations()
        self.filterLocations()
        self.createWidgets()

    def sortLocations(self) -> None:
        if self.sorting == "Name":
            self.sortedLocations = sorted(self.locations, key=lambda x: x.name)
        elif self.sorting == "Parent":
            self.sortedLocations = sorted(self.locations, key=lambda x: x.parentID)
        elif self.sorting == "Quantity":
            self.sortedLocations = sorted(self.locations, key=lambda x: x.quantity)
        elif self.sorting == "Total Price":
            self.sortedLocations = sorted(self.locations, key=lambda x: x.totalPrice)

    def filterLocations(self) -> None:
        if len(self.sortedLocations) == 0:
            raise ValueError("No components to filter")
        if self.search is None:
            return
        toRemove: list[LocationToSort] = []
        for location in self.sortedLocations:
            if self.search.lower() not in location.name.lower() and self.search.lower() not in location.shortName.lower():
                toRemove.append(location)
        for location in toRemove:
            self.sortedLocations.remove(location)

    def createWidgets(self) -> None:
        for widget in self.locationWidgets:
            widget.destroy()
        self.locationWidgets.clear()
        if len(self.sortedLocations) == 0:
            logger.warning("No locations to display")
            return
        self.columnconfigure(0, minsize=200)
        self.columnconfigure(1, minsize=100)
        self.columnconfigure(2, minsize=100)
        self.columnconfigure(3, minsize=80)
        self.columnconfigure(4, minsize=250, weight=1)
        args = {"sticky": "nw", "pady": 5}
        self.nameLabel = ctk.CTkLabel(self, text="Name")
        self.nameLabel.grid(row=0, column=0, **args)
        self.shortNameLabel = ctk.CTkLabel(self, text="Short Name")
        self.shortNameLabel.grid(row=0, column=1, **args)
        self.totalPriceLabel = ctk.CTkLabel(self, text="Total Price")
        self.totalPriceLabel.grid(row=0, column=2, **args)
        self.quantityLabel = ctk.CTkLabel(self, text="Quantity")
        self.quantityLabel.grid(row=0, column=3, **args)
        self.descriptionLabel = ctk.CTkLabel(self, text="Description")
        self.descriptionLabel.grid(row=0, column=4, **args)
        for row, location in enumerate(self.sortedLocations):
            widget = LocationWidget(self, location, self.icons, self.db)
            widget.grid(row=row+1, sticky="nw", columnspan=5, pady=5)
            self.locationWidgets.append(widget)
