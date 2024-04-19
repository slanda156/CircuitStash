from logging import getLogger


logger = getLogger(__name__)


class Location:
    def __init__(self, name: str, **args) -> None:
        self.id: int | None = args.get("id")
        self.parentID: int = args.get("parentID", -1)
        self.name = name
        self.shortName: str = args.get("shortName", "")
        self.description: str = args.get("description", "")

    @property
    def toDB(self) -> dict:
        return {
            "name": self.name,
            "parentID": self.parentID,
            "shortName": self.shortName,
            "description": self.description
        }
