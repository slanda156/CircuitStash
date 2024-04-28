from src.database import Database
from src.component import Component
from src.location import Location

db = Database()

def test_connectDb():
    assert db.connect() is True

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

def test_addComponentToLocation():
    assert db.addComponentToLocation(1, 1, 1) is True

def test_removeComponentFromLocation():
    assert db.removeComponentFromLocation(1, 1, 6) is True

def test_deleteComponent():
    component = db.getComponent(name="Test")
    assert component is not None
    assert db.deleteComponent(component) is True

def test_deleteLocation():
    location = db.getLocation(name="Test")
    assert location is not None
    assert db.deleteLocation(location) is True
