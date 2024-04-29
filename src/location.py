from logging import getLogger


logger = getLogger(__name__)


class Location:
    def __init__(self, name: str, **args) -> None:
        """
        Initialize a Location object.

        Args:
            name (str): The name of the location.
            **args: Additional keyword arguments.
                id (int, optional): The ID of the location. Defaults to None.
                parentID (int, optional): The ID of the parent location. Defaults to -1.
                shortName (str, optional): The short name of the location. Defaults to an empty string.
                description (str, optional): The description of the location. Defaults to an empty string.
        """
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
