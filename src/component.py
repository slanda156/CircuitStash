from logging import getLogger

from PIL import Image, ImageOps

from PIL.Image import Image as Img

from .location import Location
from pathlib import Path


logger = getLogger(__name__)


class Component:
    """
    Represents a component in the CircuitStash application.

    Attributes:
        id (int | None): The ID of the component.
        name (str): The name of the component.
        description (str): The description of the component.
        price (float): The price of the component.
        image (Img | None): The image of the component.
        imagePath (str | Path | None): The path to the image file of the component.
        datasheetPath (str | Path | None): The path to the datasheet file of the component.
        locations (list[tuple[Location, int]]): The list of locations where the component is available.
    """

    def __init__(self, name: str, **args) -> None:
        self.id: int | None = args.get("id")
        self.name = name
        self.description: str = args.get("description", "")
        self.price: float  = round(float(args.get("price", 0.0)), 2)
        self.image: Img | None = None
        self.imagePath: str | Path | None = args.get("imagePath")
        self.datasheetPath: str | Path | None = args.get("datasheetPath")
        self.locations: list[tuple[Location, int]] = []

        if self.imagePath and isinstance(self.imagePath, Path):
            self.imagePath = str(self.imagePath)
        if self.datasheetPath and isinstance(self.datasheetPath, Path):
            self.datasheetPath = str(self.datasheetPath)

        if self.imagePath:
            try:
                image = Image.open(self.imagePath)
                self.image = ImageOps.fit(image, (128, 128))
            except FileNotFoundError:
                logger.error(f"Image not found: {self.imagePath}")
            except Exception as e:
                logger.error(f"Error opening image: {e}")


    @property
    def toDB(self) -> dict:
        """
        Returns a dictionary representation of the component for database storage.

        Returns:
            dict: A dictionary containing the component's attributes.
        """
        return {
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "imagePath": self.imagePath,
            "datasheetPath": self.datasheetPath
        }
