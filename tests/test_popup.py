from string import punctuation
import os

import customtkinter as ctk

from src.widgets.popups import Popup
from src.database import Database

class Master(ctk.CTk):
    def __init__(self):
        self.db = Database()


if os.environ.get("DISPLAY", "") == "":
    os.environ.__setitem__("DISPLAY", ":0.0")

master = Master()
popup = Popup("Test", master.db, master=master)


def test_popup():
    popup = Popup("Test", master.db, master=master)
    assert popup.master is not None
    assert popup.db is not None

def test_getFloatFromStr_str():
    msg = "This is a test"
    assert popup.getFloatFromStr(msg) is None

def test_getFloatFromStr_float():
    msg = "1.0"
    assert popup.getFloatFromStr(msg) == 1.0

def test_getFloatFromStr_float_comma():
    msg = "1,0"
    assert popup.getFloatFromStr(msg) == 1.0

def test_getFloatFromStr_int():
    msg = "1"
    assert popup.getFloatFromStr(msg) == 1.0

def test_getFloatFromStr_float_doubledot():
    msg = "1.0.0"
    assert popup.getFloatFromStr(msg) is None

def test_getFloatFromStr_empty():
    msg = ""
    assert popup.getFloatFromStr(msg) is None

def test_getFloatFromStr_punctuation():
    for p in punctuation:
        msg = f"{p}"
        print(msg)
        assert popup.getFloatFromStr(msg) is None

def test_getIntFromStr_str():
    msg = "This is a test"
    assert popup.getIntFromStr(msg) is None

def test_getIntFromStr_int():
    msg = "1"
    assert popup.getIntFromStr(msg) == 1

def test_getIntFromStr_float():
    msg = "1.0"
    assert popup.getIntFromStr(msg) == 1

def test_getIntFromStr_float_comma():
    msg = "1,0"
    assert popup.getIntFromStr(msg) == 1

def test_getIntFromStr_float_doubledot():
    msg = "1.0.0"
    assert popup.getIntFromStr(msg) is None

def test_getIntFromStr_empty():
    msg = ""
    assert popup.getIntFromStr(msg) is None

def test_getIntFromStr_punctuation():
    for p in punctuation:
        msg = f"{p}"
        print(msg)
        assert popup.getIntFromStr(msg) is None

def test_getIdFromStr_intandstr():
    msg = "[0] Test"
    assert popup.getIdFromStr(msg) == 0
    msg = "[1] Test Test"
    assert popup.getIdFromStr(msg) == 1

def test_getIdFromStr_negintandstr():
    msg = "[-1] Test"
    assert popup.getIdFromStr(msg) == -1

def test_getIdFromStr_longnegintandstr():
    msg = "[-100] Test"
    assert popup.getIdFromStr(msg) == -100

def test_getIdFromStr_strandstr():
    msg = "[a] Test"
    assert popup.getIdFromStr(msg) is None

def test_getIdFromStr_emptyandstr():
    msg = "[] Test"
    assert popup.getIdFromStr(msg) is None

def test_getIdFromStr_punctuationandstr():
    for char in punctuation:
        msg = "[" + char +"] Test"
        print(msg)
        assert popup.getIdFromStr(msg) is None

def test_getIdFromStr_str():
    msg = "Test"
    assert popup.getIdFromStr(msg) is None

def test_getIdFromStr_empty():
    msg = ""
    assert popup.getIdFromStr(msg) is None
