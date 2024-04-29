from src.database import Database
from src.component import Component
from src.location import Location


db = Database("sqlite:///data/test_database.db")


def test_connectDb():
    assert db.connect() is True
    allComponents = db.getComponents()
    for component in allComponents:
        db.deleteComponent(component, force=True)
    assert db.getComponents() == []
    allLocations = db.getLocations()
    for location in allLocations:
        db.deleteLocation(location, force=True)
    assert db.getLocations() == []

def test_createComponent():
    component = Component("Test", description="This is a test component", price=1.0)
    assert db.createComponent(component) is True

def test_getComponents():
    assert db.getComponents() is not None

def test_createLocation():
    location = Location("Test", parentID=-1, shortName="T", description="This is a test location")
    assert db.createLocation(location) is True

def test_getLocations():
    assert db.getLocations() is not None

def test_createComponentLocationMap():
    assert db.createComponentLocationMap(1, 1, 5) is True
    assert db.getComponentAmountInLocation(1, 1) == 5

def test_addComponentToLocation():
    assert db.addComponentToLocation(1, 1, 1) is True
    assert db.getComponentAmountInLocation(1, 1) == 6

def test_removeComponentFromLocation():
    assert db.removeComponentFromLocation(1, 1, 5) is True
    assert db.getComponentAmountInLocation(1, 1) == 1

def test_deleteComponent():
    component = db.getComponent(name="Test")
    assert component is not None
    assert db.deleteComponent(component) is False
    assert db.deleteComponent(component, force=True) is True

def test_deleteLocation():
    location = db.getLocation(name="Test")
    assert location is not None
    assert db.deleteLocation(location) is True
