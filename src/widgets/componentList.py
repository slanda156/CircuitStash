from typing import TYPE_CHECKING
from logging import getLogger

import customtkinter as ctk

from src.component import Component
from src.widgets import ChangeComponent

if TYPE_CHECKING:
    from src.app import App


logger = getLogger(__name__)


class ComponentToSort(Component):
    def __init__(self, component: Component) -> None:
        super().__init__(
                            id=component.id,
                            name=component.name,
                            description=component.description,
                            price=component.price,
                            image=component.image,
                            imagePath=component.imagePath,
                            datasheetPath=component.datasheetPath,
                            locations=component.locations
                        )
        self.quantity = sum([quantity for _, quantity in self.locations])
        self.totalPrice = self.price * self.quantity


class ComponentWidget(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkScrollableFrame, component: ComponentToSort, icons: dict[str, ctk.CTkImage], master) -> None:
        super().__init__(parent)
        self.component = component
        self.icons = icons
        if self.component.image:
            self.image = ctk.CTkImage(self.component.image, size=(64, 64))
        else:
            self.image = None
        self.master: App = master
        self.db = self.master.db
        self.popup: ChangeComponent | None = None
        self.createWidgets()

    def createWidgets(self) -> None:
        self.columnconfigure(0, minsize=100)
        self.columnconfigure(1, minsize=200)
        self.columnconfigure(2, minsize=100)
        self.columnconfigure(3, minsize=100)
        self.columnconfigure(4, minsize=80)
        self.columnconfigure(5, minsize=250, weight=1)
        args = {"sticky": "nw", "padx": 5, "pady": 5}
        self.imageLabel = ctk.CTkLabel(self, text="", image=self.image)
        self.imageLabel.grid(row=0, column=0, **args)
        self.nameLabel = ctk.CTkLabel(self, text=self.component.name)
        self.nameLabel.grid(row=0, column=1, **args)
        self.priceLabel = ctk.CTkLabel(self, text=f"{self.component.price:.2f}€")
        self.priceLabel.grid(row=0, column=2, **args)
        self.totalPriceLabel = ctk.CTkLabel(self, text=f"{self.component.totalPrice:.2f}€")
        self.totalPriceLabel.grid(row=0, column=3, **args)
        self.quantityLabel = ctk.CTkLabel(self, text=f"{self.component.quantity}")
        self.quantityLabel.grid(row=0, column=4, **args)
        self.descriptionTextbox = ctk.CTkTextbox(self, width=250, height=50)
        self.descriptionTextbox.insert("1.0", self.component.description)
        self.descriptionTextbox.configure(state="disabled")
        self.descriptionTextbox.grid(row=0, column=5, **args)
        self.changeButon = ctk.CTkButton(self, text="", image=self.icons["edit-pencil"], width=28, command=self.change)
        self.changeButon.grid(row=0, column=6, **args)

    def change(self) -> None:
        logger.info(f"Changing component {self.component.name}")
        self.popup = ChangeComponent(self.component, self.db, self)
        self.popup.destroyFunc = self.destroyPopup
        self.popup.protocol("WM_DELETE_WINDOW", self.destroyPopup)
        self.popup.transient(self.master)
        self.popup.wait_visibility()
        self.popup.grab_set()
        self.popup.wait_window()

    def destroyPopup(self) -> None:
        if self.popup:
            logger.debug(f"Destroying popup, \"{self.popup.title()}\"")
            self.popup.grab_release()
            self.popup.destroy()
            self.popup = None


class ComponentList(ctk.CTkScrollableFrame):
    def __init__(self, parent: ctk.CTkBaseClass, icons: dict[str, ctk.CTkImage], components: list[Component], master, sorting: str, search: str="") -> None:
        super().__init__(parent)
        self.icons = icons
        self.master: App = master
        self.sortedComponent: list[ComponentToSort] = []
        self.componentWidgets: list[ComponentWidget] = []
        self.refresh(components, sorting, search)

    def refresh(self, components: list[Component], sorting: str, search: str) -> None:
        self.components = [ComponentToSort(component) for component in components]
        self.sorting = sorting
        self.search = search if search else None
        self.sortComponents()
        self.filterComponents()
        self.createWidgets()

    def sortComponents(self) -> None:
        if self.sorting == "Name":
            self.sortedComponent = sorted(self.components, key=lambda x: x.name)
        elif self.sorting == "Price":
            self.sortedComponent = sorted(self.components, key=lambda x: x.price)
        elif self.sorting == "Quantity":
            self.sortedComponent = sorted(self.components, key=lambda x: x.quantity)
        elif self.sorting == "Total Price":
            self.sortedComponent = sorted(self.components, key=lambda x: x.totalPrice)
        else:
            raise ValueError("Invalid sorting value")

    def filterComponents(self) -> None:
        if len(self.sortedComponent) == 0:
            raise ValueError("No components to filter")
        if self.search is None:
            return
        toRemove: list[ComponentToSort] = []
        for component in self.sortedComponent:
            if self.search.lower() not in component.name.lower():
                toRemove.append(component)
        for component in toRemove:
            self.sortedComponent.remove(component)

    def createWidgets(self) -> None:
        for widget in self.componentWidgets:
            widget.destroy()
        self.componentWidgets.clear()
        if len(self.sortedComponent) == 0:
            logger.warning("No components to display")
            return
        self.columnconfigure(0, minsize=100)
        self.columnconfigure(1, minsize=200)
        self.columnconfigure(2, minsize=100)
        self.columnconfigure(3, minsize=100)
        self.columnconfigure(4, minsize=80)
        self.columnconfigure(5, minsize=250, weight=1)
        args = {"sticky": "nw", "pady": 5}
        self.nameLabel = ctk.CTkLabel(self, text="Name")
        self.nameLabel.grid(row=0, column=1, **args)
        self.priceLabel = ctk.CTkLabel(self, text="Price")
        self.priceLabel.grid(row=0, column=2, **args)
        self.totalPriceLabel = ctk.CTkLabel(self, text="Total Price")
        self.totalPriceLabel.grid(row=0, column=3, **args)
        self.quantityLabel = ctk.CTkLabel(self, text="Quantity")
        self.quantityLabel.grid(row=0, column=4, **args)
        self.descriptionLabel = ctk.CTkLabel(self, text="Description")
        self.descriptionLabel.grid(row=0, column=5, **args)
        for row, component in enumerate(self.sortedComponent):
            widget = ComponentWidget(self, component, self.icons, self.master)
            widget.grid(row=row+1, sticky="nw", columnspan=6, pady=5)
            self.componentWidgets.append(widget)
