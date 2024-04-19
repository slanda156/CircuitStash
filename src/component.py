from logging import getLogger

from PIL.Image import Image as Img


logger = getLogger(__name__)


class Component:
    def __init__(self, name: str, **args) -> None:
        self.id: int | None = args.get("id")
        self.name = name
        self.description: str = args.get("description", "")
        self.price = args.get("price", 0.0)
        self.image: Img | None = None
        self.imagePath: str | None = args.get("imagePath")
        self.datasheetPath: str | None = args.get("datasheetPath")
        self.locations = []


    @property
    def toDB(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "imagePath": self.imagePath,
            "datasheetPath": self.datasheetPath
        }
