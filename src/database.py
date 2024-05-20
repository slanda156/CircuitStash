from logging import getLogger
from sqlmodel import create_engine, SQLModel, Session, Field, select
from sqlalchemy.exc import OperationalError

from src.component import Component
from src.location import Location


logger = getLogger(__name__)


class Components(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None
    price: float
    imagePath: str | None = None
    datasheetPath: str | None = None

    def toDict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "imagePath": self.imagePath,
            "datasheetPath": self.datasheetPath
        }


class ComponentLocationMap(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    componentID: int
    amount: int
    locationID: int

    def toDict(self) -> dict:
        return {
            "id": self.id,
            "componentID": self.componentID,
            "amount": self.amount,
            "locationID": self.locationID
        }


class Locations(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    parentID: int
    name: str
    shortName: str
    description: str

    def toDict(self) -> dict:
        return {
            "id": self.id,
            "parentID": self.parentID,
            "name": self.name,
            "shortName": self.shortName,
            "description": self.description
        }


class Database:
    def __init__(self, db: str | None = None) -> None:
        self.echo = True if logger.level == 10 else False
        if db:
            self.engineUrl = db
        else:
            self.engineUrl = "sqlite:///data/database.db"

    def connect(self) -> bool:
        try:
            self.engine = create_engine(self.engineUrl, echo=self.echo)
            SQLModel.metadata.create_all(self.engine)
            logger.info("Connected to database")
            return True
        except Exception as e:
            logger.error("Database connection error")
            logger.debug(e)
            return False

    def createComponent(self, component: Component) -> bool:
        try:
            with Session(self.engine) as session:
                stmt = select(Components).where(Components.name == component.name)
                results = session.exec(stmt).all()
                if results:
                    logger.error(f"Component \"{component.name}\" already exists")
                    return False

                newComponent = Components(**component.toDB)
                session.add(newComponent)
                session.commit()
                logger.info(f"Component \"{component.name}\" created")
                return True

        except OperationalError as e:
            logger.error("Database error")
            logger.debug(e)
            return False

    def deleteComponent(self, component: Component, force: bool=False) -> bool:
        try:
            with Session(self.engine) as session:
                stmt = select(Components).where(Components.id == component.id)
                result = session.exec(stmt).first()
                if not result:
                    logger.warning(f"Component \"{component.name}\" not found")
                    return False

                results = session.exec(select(ComponentLocationMap).where(ComponentLocationMap.componentID == component.id)).all()
                if force:
                    for result in results:
                        session.delete(result)
                elif results:
                    logger.warning(f"Component \"{component.name}\" is still in use")
                    return False

                session.delete(result)
                session.commit()
                logger.info(f"Component \"{component.name}\" deleted")
                return True

        except OperationalError as e:
            logger.error("Database error")
            logger.debug(e)
            return False

    def getComponents(self) -> list[Component]:
        try:
            with Session(self.engine) as session:
                stmt = select(Components)
                results = session.exec(stmt).all()
                components = [Component(**result.toDict()) for result in results]
                for c in components:
                    stmt = select(ComponentLocationMap).where(ComponentLocationMap.componentID == c.id)
                    results = session.exec(stmt).all()
                    for result in results:
                        loc = self.getLocation(result.locationID)
                        if not loc:
                            logger.warning(f"Location ID: \"{result.locationID}\" not found")
                            continue
                        c.locations.append((loc, result.amount))
                return components

        except OperationalError as e:
            logger.error("Database error")
            logger.debug(e)
            return []

    def getComponent(self, id: int = -1, name: str = "") -> Component | None:
        try:
            with Session(self.engine) as session:
                if id > -1:
                    stmt = select(Components).where(Components.id == id)
                elif name != "":
                    stmt = select(Components).where(Components.name == name)
                else:
                    raise ValueError("No ID or name provided")

                result = session.exec(stmt).first()
                if not result:
                    logger.warning(f"Component \"{name}\" not found")
                    return

                component = Component(**result.toDict())

                stmt = select(ComponentLocationMap).where(ComponentLocationMap.componentID == component.id)
                results = session.exec(stmt).all()
                for result in results:
                    loc = self.getLocation(result.locationID)
                    if not loc:
                        logger.warning(f"Location ID: \"{result.locationID}\" not found")
                        continue
                    component.locations.append((loc, result.amount))
                return component

        except OperationalError as e:
            logger.error("Database error")
            logger.debug(e)
            return

    def createLocation(self, location: Location) -> bool:
        try:
            with Session(self.engine) as session:
                stmt = select(Locations).where(Locations.name == location.name)
                results = session.exec(stmt).all()
                if results:
                    logger.warning(f"Location \"{location.name}\" already exists")
                    return False

                if location.parentID != -1:
                    stmt = select(Locations).where(Locations.id == location.parentID)
                    results = session.exec(stmt).all()
                    if not results:
                        logger.warning(f"Parent location ID: \"{location.parentID}\" doesn't exist")
                        return False

                newLocation = Locations(**location.toDB)
                session.add(newLocation)
                session.commit()
                logger.info(f"Location \"{location.name}\" created")
                return True

        except OperationalError as e:
            logger.error("Database error")
            logger.debug(e)
            return False

    def deleteLocation(self, location: Location, force: bool=False) -> bool:
        try:
            with Session(self.engine) as session:
                stmt = select(Locations).where(Locations.id == location.id)
                result = session.exec(stmt).first()
                if not result:
                    logger.warning(f"Location \"{location.name}\" not found")
                    return False

                results = session.exec(select(ComponentLocationMap).where(ComponentLocationMap.locationID == location.id)).all()
                if force:
                    for result in results:
                        session.delete(result)
                elif results:
                    logger.warning(f"Location \"{location.name}\" still has components")
                    return False

                session.delete(result)
                session.commit()
                logger.info(f"Location \"{location.name}\" deleted")
                return True

        except OperationalError as e:
            logger.error("Database error")
            logger.debug(e)
            return False

    def getLocations(self) -> list[Location]:
        try:
            with Session(self.engine) as session:
                stmt = select(Locations)
                results = session.exec(stmt).all()
                return [Location(**result.toDict()) for result in results]

        except OperationalError as e:
            logger.error("Database error")
            logger.debug(e)
            return []

    def getLocation(self, id: int = -1, name: str = "") -> Location | None:
        try:
            with Session(self.engine) as session:
                if id > -1:
                    stmt = select(Locations).where(Locations.id == id)
                elif name != "":
                    stmt = select(Locations).where(Locations.name == name)
                else:
                    raise ValueError("No ID or name provided")

                result = session.exec(stmt).first()
                if not result:
                    logger.warning(f"Location \"{name}\" not found")
                    return

                return Location(**result.toDict())

        except OperationalError as e:
            logger.error("Database error")
            logger.debug(e)
            return

    def createComponentLocationMap(self, componentID: int, locationID: int, amount: int) -> bool:
        try:
            with Session(self.engine) as session:
                stmt = select(ComponentLocationMap).where(ComponentLocationMap.componentID == componentID, ComponentLocationMap.locationID == locationID)
                results = session.exec(stmt).all()
                if results:
                    logger.warning(f"Component ID: \"{componentID}\" already exists in location ID: \"{locationID}\"")
                    return False

                newMap = ComponentLocationMap(componentID=componentID, locationID=locationID, amount=amount)
                session.add(newMap)
                session.commit()
                logger.info(f"Component ID: \"{componentID}\" added to location ID: \"{locationID}\"")
                return True

        except OperationalError as e:
            logger.error("Database error")
            logger.debug(e)
            return False

    def addComponentToLocation(self, componentID: int, locationID: int, amount: int) -> bool:
        try:
            with Session(self.engine) as session:
                stmt = select(ComponentLocationMap).where(ComponentLocationMap.componentID == componentID, ComponentLocationMap.locationID == locationID)
                result = session.exec(stmt).first()
                if not result:
                    logger.warning(f"Component ID: \"{componentID}\" not found in location ID: \"{locationID}\"")
                    return False

                result.amount += amount
                session.add(result)
                session.commit()
                logger.info(f"Component ID: \"{componentID}\" amount in location ID: \"{locationID}\" increased by {amount}")
                return True

        except OperationalError as e:
            logger.error("Database error")
            logger.debug(e)
            return False

    def removeComponentFromLocation(self, componentID: int, locationID: int, amount: int) -> bool:
        try:
            with Session(self.engine) as session:
                stmt = select(ComponentLocationMap).where(ComponentLocationMap.componentID == componentID, ComponentLocationMap.locationID == locationID)
                result = session.exec(stmt).first()
                if not result:
                    logger.warning(f"Component ID: \"{componentID}\" not found in location ID: \"{locationID}\"")
                    return False

                if result.amount < amount:
                    logger.warning(f"Component ID: \"{componentID}\" amount in location ID: \"{locationID}\" is less than {amount}")
                    return False

                if result.amount == amount:
                    session.delete(result)
                    session.commit()
                    return True

                result.amount -= amount
                session.add(result)
                session.commit()
                logger.info(f"Component ID: \"{componentID}\" amount in location ID: \"{locationID}\" decreased by {amount}")
                return True

        except OperationalError as e:
            logger.error("Database error")
            logger.debug(e)
            return False

    def getComponentLocationMap(self, componentID: int=-1, locationID: int=-1, clmId: int=-1) -> ComponentLocationMap | None:
        try:
            if clmId > -1:
                with Session(self.engine) as session:
                    stmt = select(ComponentLocationMap).where(ComponentLocationMap.id == clmId)
                    result = session.exec(stmt).first()
                    if not result:
                        logger.warning(f"ComponentLocationMap ID: \"{clmId}\" not found")
                        return
                    return ComponentLocationMap(**result.toDict())
            elif componentID > -1 and locationID > -1:
                with Session(self.engine) as session:
                    stmt = select(ComponentLocationMap).where(ComponentLocationMap.componentID == componentID, ComponentLocationMap.locationID == locationID)
                    result = session.exec(stmt).first()
                    if not result:
                        logger.warning(f"Component \"{componentID}\" not found in location \"{locationID}\"")
                        return
                    return ComponentLocationMap(**result.toDict())
            else:
                raise ValueError("No ID provided")

        except OperationalError as e:
            logger.error("Database error")
            logger.debug(e)

    def getComponentAmountInLocation(self, componentID: int, locationID: int) -> int:
        CAmap = self.getComponentLocationMap(componentID, locationID)
        if CAmap:
            return CAmap.amount
        else:
            return -1

    def getComponentsInLocation(self, locationID: int) -> list[Component]:
        try:
            with Session(self.engine) as session:
                stmt = select(ComponentLocationMap).where(ComponentLocationMap.locationID == locationID)
                results = session.exec(stmt).all()
                components: list[Component] = []
                for result in results:
                    component = self.getComponent(result.componentID)
                    if component:
                        components.append(component)
                return components

        except OperationalError as e:
            logger.error("Database error")
            logger.debug(e)
            return []

    def getLocationsIdForComponent(self, componentID: int) -> list[tuple[int, int]]:
        try:
            with Session(self.engine) as session:
                stmt = select(ComponentLocationMap).where(ComponentLocationMap.componentID == componentID)
                results = session.exec(stmt).all()
                return [(result.locationID, result.amount) for result in results]

        except OperationalError as e:
            logger.error("Database error")
            logger.debug(e)
            return []

    def getLocationsForComponent(self, componentID: int) -> list[tuple[Location, int]]:
        data = self.getLocationsIdForComponent(componentID)
        locations = []
        for locationID, amount in data:
            loc = self.getLocation(locationID)
            if loc:
                locations.append((loc, amount))
        return locations


    def getAllComponentAmount(self, componentID: int) -> int:
        try:
            with Session(self.engine) as session:
                stmt = select(ComponentLocationMap).where(ComponentLocationMap.componentID == componentID)
                results = session.exec(stmt).all()
                amount = 0 if results else -1
                for result in results:
                    amount += result.amount
                return amount

        except OperationalError as e:
            logger.error("Database error")
            logger.debug(e)
            return -1
