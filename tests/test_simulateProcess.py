import pytest
import pandas as pd
import os
from simulateProcess import (
    evaluateAlarms,
    generateProcessSnapshot,
    snapshotToDict,
    appendSnapshot,
    initializeCSV,
    getNextBatchID,
    runSimulatorLoop
)

# -------------------------------------
# Constants
# -------------------------------------

DATA_FILE_PATH = "tests/test_data.csv"


# -------------------------------------
# Core Testing
# -------------------------------------

def test_evaluateAlarms_no_alarms():
    alarmsTriggered, alarmType = evaluateAlarms(do=30.0, temp=37.0, ph=7.0)
    assert alarmsTriggered == False
    assert alarmType == ""


def test_evaluateAlarms_DOOutOfRange_high():
    alarmsTriggered, alarmType = evaluateAlarms(do=55.1, temp=37.0, ph=7.0)
    assert alarmsTriggered == True
    assert "DOOutOfRange" in alarmType


def test_evaluateAlarms_DOOutOfRange_low():
    alarmsTriggered, alarmType = evaluateAlarms(do=19.9, temp=37.0, ph=7.0)
    assert alarmsTriggered == True
    assert "DOOutOfRange" in alarmType


def test_evaluateAlarms_multiple_alarms():
    alarmsTriggered, alarmType = evaluateAlarms(do=19.0, temp=41.0, ph=8.0)
    assert alarmsTriggered == True
    assert "DOOutOfRange" in alarmType
    assert "HighTemp" in alarmType
    assert "pHOutOfRange" in alarmType


def test_generateProcessSnapshot_keys_and_types():
    snapshot = generateProcessSnapshot(batchID=1, timeStamp="2025-01-01 12:00:00")
    assert isinstance(snapshot, dict)
    expected_keys = {
        "Timestamp", "BatchID", "DissolvedOxygen",
        "Temperature", "pH", "Yield", "AlarmTriggered", "AlarmType"
    }
    assert set(snapshot.keys()) == expected_keys
    assert isinstance(snapshot["BatchID"], int)
    assert isinstance(snapshot["DissolvedOxygen"], float)
    assert isinstance(snapshot["Temperature"], float)
    assert isinstance(snapshot["pH"], float)
    assert isinstance(snapshot["Yield"], float)
    assert isinstance(snapshot["AlarmTriggered"], int)
    assert isinstance(snapshot["AlarmType"], str)


def test_snapshotToDict_structure():
    d = snapshotToDict(
        time="2025-01-01 12:00:00",
        batchID=1,
        do=50.0,
        temp=37.0,
        ph=7.0,
        productYield=4.0, 
        alarmsTriggered=True,
        alarmType="HighTemp"
    )
    assert d["Timestamp"] == "2025-01-01 12:00:00"
    assert d["BatchID"] == 1
    assert d["DissolvedOxygen"] == 50.0
    assert d["Temperature"] == 37.0
    assert d["pH"] == 7.0
    assert d["Yield"] == 4.0
    assert d["AlarmTriggered"] == 1
    assert d["AlarmType"] == "HighTemp"


def test_appendSnapshot_creates_file(filePath = DATA_FILE_PATH):
    snapshot = snapshotToDict(
        time="2025-01-01 12:00:00",
        batchID=1,
        do=50.0,
        temp=37.0,
        ph=7.0,
        productYield=4.0,
        alarmsTriggered=True,
        alarmType="HighTemp"
    )
    initializeCSV(True, filePath)
    appendSnapshot(snapshot, filePath)

    df = pd.read_csv(filePath)
    assert set(df.columns) == {
        "Timestamp", "BatchID", "DissolvedOxygen",
        "Temperature", "pH", "Yield", "AlarmTriggered", "AlarmType(s)"
    }
    assert df.shape[0] == 1
    assert df.iloc[0]["BatchID"] == 1
    assert df.iloc[0]["AlarmType(s)"] == "HighTemp"


# -------------------------------------
# Testing after the simulate single batch function included
# -------------------------------------

def test_initializeCSV_wipe_true():
    initializeCSV(True, filePath=DATA_FILE_PATH)
    assert os.path.exists(DATA_FILE_PATH)
    with open(DATA_FILE_PATH) as f:
        content = f.read()
    assert "Timestamp,BatchID" in content

def test_initializeCSV_wipe_false_new_file():
    # Remove it first if it exists
    if os.path.exists(DATA_FILE_PATH):
        os.remove(DATA_FILE_PATH)
    initializeCSV(False, filePath=DATA_FILE_PATH)
    assert os.path.exists(DATA_FILE_PATH)
    with open(DATA_FILE_PATH) as f:
        content = f.read()
    assert "Timestamp,BatchID" in content

def test_initializeCSV_wipe_false_existing_file():
    with open(DATA_FILE_PATH, "w") as f:
        f.write("keep me")
    initializeCSV(False, filePath=DATA_FILE_PATH)
    with open(DATA_FILE_PATH) as f:
        content = f.read()
    assert "keep me" in content

def test_getNextBatchID_existing():
    df = pd.DataFrame({"BatchID": [1, 2, 3]})
    df.to_csv(DATA_FILE_PATH, index=False)
    assert getNextBatchID(DATA_FILE_PATH) == 4

def test_getNextBatchID_empty():
    with open(DATA_FILE_PATH, "w") as f:
        f.write("")
    assert getNextBatchID(DATA_FILE_PATH) == 1

def test_getNextBatchID_missing():
    if os.path.exists(DATA_FILE_PATH):
        os.remove(DATA_FILE_PATH)
    assert getNextBatchID(DATA_FILE_PATH) == 1

def test_runSimulatorLoop_wipe_true():
    runSimulatorLoop(3, True, DATA_FILE_PATH)
    df = pd.read_csv(DATA_FILE_PATH)
    assert df.shape[0] == 3
    assert df.iloc[0]['BatchID'] == 1

def test_runSimulatorLoop_wipe_false():
    runSimulatorLoop(1, True, DATA_FILE_PATH)
    runSimulatorLoop(2, False, DATA_FILE_PATH)
    df = pd.read_csv(DATA_FILE_PATH)
    assert df.shape[0] == 3
    assert df.iloc[-1]['BatchID'] == 3