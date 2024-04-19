from logging import getLogger
from sqlmodel import create_engine, SQLModel, Session, Field, select
from sqlalchemy.exc import OperationalError

from src.component import Component


logger = getLogger(__name__)


class Components(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None
    price: float
    imagePath: str | None = None
    datasheetPath: str | None = None


class ComponentLocationMap(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    componentID: int
    amount: int


class Locations(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    parentID: int
    name: str
    shortName: str
    description: str
    componentID: int


class Database:
    def __init__(self) -> None:
        self.echo = True if logger.level == 10 else False
        self.engineUrl = "sqlite:///data/database.db"

    def connect(self) -> None:
        self.engine = create_engine(self.engineUrl, echo=self.echo)
        SQLModel.metadata.create_all(self.engine)
        logger.info("Connected to database")

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
