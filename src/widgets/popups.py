from logging import getLogger
from pathlib import Path

import customtkinter as CTk
import tkinter.filedialog as tkfd
from PIL import Image

from ..database import Database
from ..component import Component
from ..location import Location


logger = getLogger(__name__)


class Popup(CTk.CTkToplevel):
    def __init__(self, tile: str, db: Database,  *args, **kargs) -> None:
        super().__init__(*args, **kargs)
        self.title(tile)
        self.resizable(False, False)
        self.db: Database = db
        self.destroyFunc = self._destroy
        self.createWidgets()

    def createWidgets(self) -> None:
        pass

    def _destroy(self) -> None:
        raise ValueError("This method must be overridden")

    def getFloatFromStr(self, s: str) -> float | None:
        s = s.replace("€", "").replace(",", ".").strip()
        if s == "":
            logger.debug("Empty string input")
            return
        if len(s) == 1 and not s.isdigit():
            logger.debug("Invalid string input")
            return
        if s.count(".") > 1:
            logger.debug("Invalid string input")
            return
        for char in s:
            if not char.isdigit() and char != ".":
                logger.debug("Invalid string input")
                return
        f = float(s)
        return f

    def getIntFromStr(self, s: str) -> int | None:
        f = self.getFloatFromStr(s)
        if f:
            return int(f)

    def getIdFromStr(self, s: str) -> int | None:
        if s == "":
            logger.debug("Empty string input")
            return
        if len(s) < 3:
            logger.debug("Invalid string input")
            return
        start = s.find("[")
        stop = s.find("]")
        if start == -1 or stop == -1:
            logger.debug("Invalid string input")
            return
        s = s[start+1:stop]
        if not (s.isdigit() or (s[1:].isdigit() and s[0] == "-")):
            logger.debug("Invalid string input")
            return
        return int(s)

class AddComponentLocation(Popup):
    def __init__(self, db: Database, *args, **kargs) -> None:
        super().__init__("Add Component to Location", db, *args, **kargs)

    def createWidgets(self) -> None:
        self.componentLabel = CTk.CTkLabel(self, text="Component: ")
        self.componentLabel.grid(row=0, column=0, sticky="e")
        self.componentValues = [f"[{component.id}] {component.name}" for component in self.db.getComponents()]
        self.componentVar = CTk.StringVar(self)
        self.componentOptionMenu = CTk.CTkOptionMenu(self, variable=self.componentVar, values=self.componentValues, command=self.refreshCurrentAmount)
        self.componentOptionMenu.bind("<FocusOut>", self.refreshCurrentAmount)
        self.componentOptionMenu.grid(row=0, column=1)
        self.locationLabel = CTk.CTkLabel(self, text="Location: ")
        self.locationLabel.grid(row=1, column=0, sticky="e")
        self.locationValues = [f"[{location.id}] {location.shortName}" for location in self.db.getLocations()]
        self.locationVar = CTk.StringVar(self)
        self.locationOptionMenu = CTk.CTkOptionMenu(self, variable=self.locationVar, values=self.locationValues, command=self.refreshCurrentAmount)
        self.locationOptionMenu.grid(row=1, column=1)
        self.amountLabel = CTk.CTkLabel(self, text="Amount: ")
        self.amountLabel.grid(row=2, column=0, sticky="e")
        self.amountEntry = CTk.CTkEntry(self)
        self.amountEntry.bind("<Return>", self.add)
        self.amountEntry.grid(row=2, column=1)
        self.currentAmountLabel = CTk.CTkLabel(self, text="Current Amount: ")
        self.currentAmountLabel.grid(row=3, column=0, sticky="e")
        self.currentAmountLabelValue = CTk.CTkLabel(self, text="0")
        self.currentAmountLabelValue.grid(row=3, column=1, sticky="w")
        self.cancleButton = CTk.CTkButton(self, text="Cancel", command=lambda: self.destroyFunc())
        self.cancleButton.grid(row=4, column=0)
        self.addButton = CTk.CTkButton(self, text="Add", command=self.add)
        self.addButton.grid(row=4, column=1)

    def refreshCurrentAmount(self, *args) -> None:
        componentId = self.getIdFromStr(self.componentVar.get())
        locationId = self.getIdFromStr(self.locationVar.get())
        if componentId is None or componentId < 0:
            return
        if locationId is None or locationId < 0:
            return
        currentAmount = self.db.getComponentAmountInLocation(componentId, locationId)
        logger.debug(f"Refreshing current amount, component: {componentId}, location: {locationId}, amount: {currentAmount}")
        self.currentAmountLabel.configure(text=str(currentAmount))

    def add(self, *args) -> None:
        componentId = self.getIdFromStr(self.componentVar.get())
        locationId = self.getIdFromStr(self.locationVar.get())
        amount = self.getIntFromStr(self.amountEntry.get())
        if componentId is None or componentId < 0:
            logger.warning("Invalid component input")
            self.componentOptionMenu.focus_set()
            self.componentOptionMenu.configure(fg_color="red")
            return
        if locationId is None or locationId < 0:
            logger.warning("Invalid location input")
            self.locationOptionMenu.focus_set()
            self.locationOptionMenu.configure(fg_color="red")
            return
        if amount is None or amount <= 0:
            logger.warning("Invalid amount input")
            self.amountEntry.focus_set()
            self.amountEntry.configure(fg_color="red")
            return
        componentLocation = {
            "componentID": componentId,
            "locationID": locationId,
            "amount": amount
        }
        if not self.db.addComponentToLocation(**componentLocation):
            if not self.db.createComponentLocationMap(**componentLocation):
                logger.error("Failed to add component to location")
                return
        logger.debug(f"Adding component to location, \"{self.componentVar.get()}\" to \"{self.locationVar.get()}\", amount: {self.amountEntry.get()}")
        self.destroyFunc()


class AddComponent(Popup):
    def __init__(self, db: Database, *args, **kargs) -> None:
        super().__init__("Add Component", db, *args, **kargs)
        self.imagePath: Path | None = None
        self.datasheetPath: Path | None = None

    def createWidgets(self) -> None:
        self.nameLabel = CTk.CTkLabel(self, text="Name: ")
        self.nameLabel.grid(row=0, column=0, sticky="e")
        self.nameEntry = CTk.CTkEntry(self, width=160)
        self.nameEntry.grid(row=0, column=1, sticky="w")
        self.priceLabel = CTk.CTkLabel(self, text="Price: ")
        self.priceLabel.grid(row=1, column=0, sticky="e")
        self.priceEntry = CTk.CTkEntry(self, width=70, placeholder_text=" €")
        self.priceEntry.bind("<FocusOut>", self.addCurrency)
        self.priceEntry.grid(row=1, column=1, sticky="w")
        self.imageLabel = CTk.CTkLabel(self, text="Image: ")
        self.imageLabel.grid(row=2, column=0, sticky="e")
        self.imageEntry = CTk.CTkEntry(self, width=300)
        self.imageEntry.grid(row=2, column=1)
        self.imageButton = CTk.CTkButton(self, text="Select Image", command=self.createImageDialog)
        self.imageButton.grid(row=2, column=2)
        self.datasheetLabel = CTk.CTkLabel(self, text="Datasheet: ")
        self.datasheetLabel.grid(row=3, column=0, sticky="e")
        self.datasheetEntry = CTk.CTkEntry(self, width=300)
        self.datasheetEntry.grid(row=3, column=1)
        self.datasheetButton = CTk.CTkButton(self, text="Select Datasheet", command=self.createDatasheetDialog)
        self.datasheetButton.grid(row=3, column=2)
        self.descriptionLabel = CTk.CTkLabel(self, text="Description: ")
        self.descriptionLabel.grid(row=4, column=0, sticky="ne")
        self.descriptionTextbox = CTk.CTkTextbox(self, width=300, height=160)
        self.descriptionTextbox.grid(row=4, column=1, columnspan=3, sticky="nw")
        self.cancelButton = CTk.CTkButton(self, text="Cancel", command=lambda: self.destroyFunc())
        self.cancelButton.grid(row=5, column=0)
        self.addButton = CTk.CTkButton(self, text="Add", command=self.add)
        self.addButton.grid(row=5, column=1)

    def createImageDialog(self) -> None:
        self.imageDialog = tkfd.askopenfiles(mode="r", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")], title="Select Image", initialdir=".")
        try:
            imgPath = Path(self.imageDialog[0].name)
        except Exception as e:
            logger.warning("No image selected")
            logger.debug(e)
            return
        image = Image.open(imgPath)
        # Check if its a premade image
        if len(list(self.master.preMadePath.glob(imgPath.name))) == 0:  # type: ignore
            self.imagePath = self.master.imgPath / imgPath.name  # type: ignore
            # Check if the image is allready in the image folder
            if Path(imgPath) != self.imagePath:
                image.save(self.imagePath)
        ctkImage = CTk.CTkImage(image, size=(100, 100))
        self.image = CTk.CTkLabel(self, text="", image=ctkImage)
        self.image.grid(row=4, column=2, sticky="ne")
        self.imageEntry.delete(0, "end")
        self.imageEntry.insert("end", imgPath)

    def createDatasheetDialog(self) -> None:
        self.datasheetDialog = tkfd.askopenfiles(mode="r", filetypes=[("PDF Files", "*.pdf")], title="Select Datasheet", initialdir=".")
        try:
            name = self.datasheetDialog[0].name
        except Exception as e:
            logger.warning("No datasheet selected")
            logger.debug(e)
            return
        with open(name, "rb") as f:
            doc = f.readlines()
        self.datasheetPath = self.master.docsPath / Path(name).name  # type: ignore
        with open(self.datasheetPath, "wb") as f:
            f.writelines(doc)
        self.datasheetEntry.delete(0, "end")
        self.datasheetEntry.insert("end", name)

    def add(self, *args) -> None:
        if self.nameEntry.get() == "":
            logger.warning("Invalid name input")
            self.nameEntry.focus_set()
            self.nameEntry.configure(fg_color="red")
            return
        name = self.nameEntry.get()
        description = self.descriptionTextbox.get("1.0", "end")
        price = self.getFloatFromStr(self.priceEntry.get())
        if price is None:
            price = 0.0

        component = Component(name, description=description, price=price, imagePath=self.imagePath, datasheetPath=self.datasheetPath)
        if not self.db.createComponent(component):
            logger.error("Failed to add component")
            return
        logger.debug(f"Adding component, \"{component.name}\"")
        self.destroyFunc()

    def addCurrency(self, *args) -> None:
        event = args[0]
        try:
            widget: CTk.CTkEntry = event.widget
            if widget.widgetName != "entry":
                logger.error("Invalid widget")
                return
        except Exception as e:
            logger.error("Invalid widget")
            logger.debug(e)
            return
        price = self.getFloatFromStr(widget.get())
        if price is None:
            logger.warning("Invalid price input")
            widget.delete(0, "end")
            return
        widget.delete(0, "end")
        widget.insert(0, f"{price:.2f} €")


class AddLocation(Popup):
    def __init__(self, db: Database, *args, **kargs) -> None:
        super().__init__("Add Location", db, *args, **kargs)

    def createWidgets(self) -> None:
        self.nameLabel = CTk.CTkLabel(self, text="Name: ")
        self.nameLabel.grid(row=0, column=0, sticky="e")
        self.nameEntry = CTk.CTkEntry(self, width=160)
        self.nameEntry.grid(row=0, column=1, sticky="w")
        self.shortNameLabel = CTk.CTkLabel(self, text="Short Name: ")
        self.shortNameLabel.grid(row=1, column=0, sticky="e")
        self.shortNameEntry = CTk.CTkEntry(self, width=50)
        self.shortNameEntry.grid(row=1, column=1, sticky="w")
        self.parentLabel = CTk.CTkLabel(self, text="Parent Location: ")
        self.parentLabel.grid(row=2, column=0, sticky="e")
        self.parentValues = [f"[{location.id}] {location.shortName}" for location in self.db.getLocations()]
        self.parentValues.insert(0, "None")
        self.parentVar = CTk.StringVar(self, "None")
        self.parentOptionMenu = CTk.CTkOptionMenu(self, variable=self.parentVar, values=self.parentValues)
        self.parentOptionMenu.grid(row=2, column=1, sticky="w")
        self.desciptionLabel = CTk.CTkLabel(self, text="Description: ")
        self.desciptionLabel.grid(row=3, column=0, sticky="ne")
        self.descriptionTextbox = CTk.CTkTextbox(self, width=250, height=160)
        self.descriptionTextbox.grid(row=3, column=1, sticky="w")
        self.cancelButton = CTk.CTkButton(self, text="Cancel", command=lambda: self.destroyFunc())
        self.cancelButton.grid(row=4, column=0)
        self.addButton = CTk.CTkButton(self, text="Add", command=self.add)
        self.addButton.grid(row=4, column=1)

    def add(self) -> None:
        name = self.nameEntry.get()
        shortName = self.shortNameEntry.get()
        parent = self.parentVar.get()
        if parent == "None":
            parent = -1
        elif parent != "":
            parent = int(parent.split(" ")[0][1:-1])
        else:
            parent = -1
            logger.warning("Invalid parent input")
            logger.debug(f"Parent: {parent}")
        description = self.descriptionTextbox.get("1.0", "end")
        if name == "":
            logger.warning("Invalid name input")
            self.nameEntry.focus_set()
            self.nameEntry.configure(fg_color="red")
            return
        if shortName == "":
            logger.warning("Invalid short name input")
            self.shortNameEntry.focus_set()
            self.shortNameEntry.configure(fg_color="red")
            return
        location = Location(name, shortName=shortName, parentID=parent, description=description)
        if not self.db.createLocation(location):
            logger.error("Failed to add location")
            return
        logger.debug(f"Adding location, \"{location.name}\"")
        self.destroyFunc()


class ChangeComponentLocation(Popup):
    def __init__(self, id: int, db: Database, *args, **kargs) -> None:
        if id < 0:
            raise ValueError("Invalid id")
        self.id = id
        clm = self.db.getComponentLocationMap(clmId=id)
        if not clm:
            raise ValueError("Invalid id")
        componentId = clm["componentID"]
        locationId = clm["locationID"]
        self.amount = clm["amount"]
        self.component = self.db.getComponent(componentId)
        if self.component is None:
            logger.error("Invalid component id")
            self.destroyFunc()
        self.location = self.db.getLocation(locationId)
        if self.location is None:
            logger.error("Invalid location id")
            self.destroyFunc()
        super().__init__("Change Component from Location", db, *args, **kargs)

    def createWidgets(self) -> None:
        self.nameLabel = CTk.CTkLabel(self, text="Name: ")
        self.nameLabel.grid(row=0, column=0, sticky="e")
        self.nameEntry = CTk.CTkEntry(self, width=160)
        self.nameEntry.insert("end", self.component.name)
        self.nameEntry.configure(state="disabled")
        self.nameEntry.grid(row=0, column=1, sticky="w")
        self.locationLabel = CTk.CTkLabel(self, text="Location: ")
        self.locationLabel.grid(row=1, column=0, sticky="e")
        self.locationEntry = CTk.CTkEntry(self, width=160)
        self.locationEntry.insert("end", self.location.name)
        self.locationEntry.configure(state="disabled")
        self.locationEntry.grid(row=1, column=1, sticky="w")
        self.amountLabel = CTk.CTkLabel(self, text="Amount: ")
        self.amountLabel.grid(row=2, column=0, sticky="e")
        self.amountEntry = CTk.CTkEntry(self)
        self.amountEntry.insert("end", self.amount)
        self.amountEntry.configure(state="disabled")
        self.amountEntry.grid(row=2, column=1)
        self.changeAmountLabel = CTk.CTkLabel(self, text="Change Amount: ")
        self.changeAmountLabel.grid(row=3, column=0, sticky="e")
        self.changeAmountEntry = CTk.CTkEntry(self)
        self.changeAmountEntry.grid(row=3, column=1)
        self.cancelButton = CTk.CTkButton(self, text="Cancel", command=lambda: self.destroyFunc())
        self.cancelButton.grid(row=4, column=0)
        self.deleteButton = CTk.CTkButton(self, text="Delete", command=self.delete)
        self.deleteButton.grid(row=4, column=1)
        self.changeButton = CTk.CTkButton(self, text="Change", command=self.change)
        self.changeButton.grid(row=4, column=2)

    def delete(self, *args) -> None:
        currentAmount = self.db.getComponentAmountInLocation(self.component.id, self.location.id)
        if not currentAmount:
            logger.error("Failed to get current amount")
            return
        if not self.db.removeComponentFromLocation(self.component.id, self.location.id, currentAmount):
            logger.error("Failed to remove component from location")
            return
        logger.debug(f"Removing component from location, \"{self.component.name}\" from \"{self.location.name}\"")
        self.destroyFunc()

    def change(self, *args) -> None:
        amount = self.getIntFromStr(self.changeAmountEntry.get())
        if not amount or amount == 0:
            logger.warning("Invalid amount (0)")
            self.changeAmountEntry.focus_set()
            self.changeAmountEntry.configure(fg_color="red")
            return
        elif amount < 0:
            self.db.removeComponentFromLocation(self.component.id, self.location.id, abs(amount))
        elif amount > 0:
            self.db.addComponentToLocation(self.component.id, self.location.id, amount)
        else:
            logger.error("Invalid amount")
            return
        logger.debug(f"Changing component amount in location, \"{self.component.name}\" in \"{self.location.name}\", amount: {amount}")
        self.destroyFunc()

class ChangeComponent(Popup):
    def __init__(self, component: Component | int, *args, **kargs) -> None:
        super().__init__("Change Component", *args, **kargs)
        if isinstance (component, int):
            self.component = self.db.getComponent(component)
        else:
            self.component = component
        if self.component is None:
            logger.error("Invalid component")
            self.destroyFunc()

    def createWidgets(self) -> None:
        pass


class ChangeLocation(Popup):
    def __init__(self, location: Location | int, db: Database, *args, **kargs) -> None:
        super().__init__("Change Location", db, *args, **kargs)
        if isinstance(location, int):
            self.location = self.db.getLocation(location)
        else:
            self.location = location
        if self.location is None:
            logger.error("Invalid location")
            self.destroyFunc()

    def createWidgets(self) -> None:
        pass
