from logging import getLogger


logger = getLogger(__name__)


class Location:
    """
    Represents a location in the system.

    Attributes:
        name (str): The name of the location.
        id (int | None): The ID of the location.
        parentID (int): The ID of the parent location.
        shortName (str): The short name of the location.
        description (str): The description of the location.
    """

    def __init__(self, name: str, **args) -> None:
        self.id: int | None = args.get("id")
        self.parentID: int = args.get("parentID", -1)
        self.name = name
        self.shortName: str = args.get("shortName", "")
        self.description: str = args.get("description", "")

    @property
    def toDB(self) -> dict:
        """
        Converts the Location object to a dictionary representation suitable for storing in a database.

        Returns:
            dict: A dictionary containing the name, parentID, shortName, and description of the Location.
        """
        return {
            "name": self.name,
            "parentID": self.parentID,
            "shortName": self.shortName,
            "description": self.description
        }
