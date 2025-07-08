import pytest
import pandas as pd
from simulateProcess import (
    evaluateAlarms,
    generateProcessSnapshot,
    snapshotToDict,
    appendSnapshot,
    initializeCSV
)

# -------------------------------------
# Constants
# -------------------------------------

DATA_FILE_PATH = "tests/test_data.csv"


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
    snapshot = generateProcessSnapshot(batchID=1)
    assert isinstance(snapshot, dict)
    expected_keys = {
        "Timestamp", "BatchID", "DissolvedOxygen",
        "Temperature", "pH", "AlarmTriggered", "AlarmType"
    }
    assert set(snapshot.keys()) == expected_keys
    assert isinstance(snapshot["BatchID"], int)
    assert isinstance(snapshot["DissolvedOxygen"], float)
    assert isinstance(snapshot["Temperature"], float)
    assert isinstance(snapshot["pH"], float)
    assert isinstance(snapshot["AlarmTriggered"], int)
    assert isinstance(snapshot["AlarmType"], str)


def test_snapshotToDict_structure():
    d = snapshotToDict(
        time="2025-01-01 12:00:00",
        batchID=1,
        do=50.0,
        temp=37.0,
        ph=7.0,
        alarmsTriggered=True,
        alarmType="HighTemp"
    )
    assert d["Timestamp"] == "2025-01-01 12:00:00"
    assert d["BatchID"] == 1
    assert d["DissolvedOxygen"] == 50.0
    assert d["AlarmTriggered"] == 1
    assert d["AlarmType"] == "HighTemp"


def test_appendSnapshot_creates_file(filePath = DATA_FILE_PATH):
    snapshot = snapshotToDict(
        time="2025-01-01 12:00:00",
        batchID=1,
        do=50.0,
        temp=37.0,
        ph=7.0,
        alarmsTriggered=True,
        alarmType="HighTemp"
    )
    initializeCSV(filePath)
    appendSnapshot(snapshot, filePath)

    df = pd.read_csv(filePath)
    assert set(df.columns) == {
        "Timestamp", "BatchID", "DissolvedOxygen",
        "Temperature", "pH", "AlarmTriggered", "AlarmType(s)"
    }
    assert df.shape[0] == 1
    assert df.iloc[0]["BatchID"] == 1
    assert df.iloc[0]["AlarmType(s)"] == "HighTemp"
