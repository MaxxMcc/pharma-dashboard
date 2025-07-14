#simulateProcess.py

import pandas as pd
import random
import datetime
import time
import os

# -------------------------------------
# Constants
# -------------------------------------

DATA_FILE_PATH = "data/batch_data.csv"

DO_HIGH_THRESHOLD = 50.0
DO_LOW_THRESHOLD = 20.0
TEMP_HIGH_THRESHOLD = 40.0
PH_LOW_THRESHOLD = 6.5
PH_HIGH_THRESHOLD = 7.5

# Simulated start date: exactly 1 year ago, new batch each 24 hours
SIMULATION_START_DATE = datetime.datetime.now() - datetime.timedelta(days=365)
BATCH_INTERVAL_HOURS = 24

# -------------------------------------
# Core Functions
# -------------------------------------

def runSimulatorLoop(batchCount: int = 60, wipeCSV: bool = True, filePath: str = DATA_FILE_PATH):
    """
    - Generate fake timestamp, process variables, alarm conditions
    - If wipeCSV is True, clear file and start BatchID at 1.
    - Else, append to existing CSV, find latest BatchID, continue.
    """
    initializeCSV(wipeCSV, filePath)
    for i in range(max(0,batchCount)):
        batchID = getNextBatchID(filePath)
        timeStamp = getNextTimeStamp(filePath)
        snapshot = generateProcessSnapshot(batchID, timeStamp)
        appendSnapshot(snapshot, filePath)


def initializeCSV(wipeCSV: bool, filePath: str = DATA_FILE_PATH):
    """
    - If wipeCSV is True or /data does not exist, wipe the file and write header.
    """
    os.makedirs(os.path.dirname(filePath), exist_ok=True)
    if wipeCSV or not os.path.exists(filePath):
        with open(filePath, mode="w") as f:
            f.write("Timestamp,BatchID,DissolvedOxygen,Temperature,pH,Yield,AlarmTriggered,AlarmType(s)\n")

def getNextBatchID(filePath: str = DATA_FILE_PATH) -> int:
    """
    Get the next BatchID based on the existing data.
    If file does not exist or is empty, return 1.
    """
    try:
        df = pd.read_csv(filePath)
        if not df.empty and 'BatchID' in df.columns:
            return df['BatchID'].iloc[-1] + 1
    except (FileNotFoundError, pd.errors.EmptyDataError, KeyError, IndexError):
        pass
    return 1

def getNextTimeStamp(filePath: str = DATA_FILE_PATH) -> int:
    """
    Get the timestamp based on the existing data.
    If file does not exist or is empty, return simulation start time.
    """
    try:
        df = pd.read_csv(filePath)
        if not df.empty and 'Timestamp' in df.columns:
            lastBatchTime = pd.to_datetime(df['Timestamp'].iloc[-1])
            return (lastBatchTime + datetime.timedelta(hours=BATCH_INTERVAL_HOURS)).strftime('%Y-%m-%d %H:%M:%S')
    except (FileNotFoundError, pd.errors.EmptyDataError, KeyError, IndexError):
        pass
    return SIMULATION_START_DATE.strftime('%Y-%m-%d %H:%M:%S')

def generateProcessSnapshot(batchID: int, timeStamp: str) -> dict:
    """Generate a single process snapshot with timestamp and variable values."""
    DissolvedOxygen = random.uniform(18, 52) #(%)
    Temperature = random.uniform(30, 42)    #(°C)
    pH = random.uniform(6.4, 7.6)
    AlarmTriggered, AlarmType = evaluateAlarms(DissolvedOxygen, Temperature, pH)
    Yield = getYield(AlarmTriggered, AlarmType) #(g)
    return snapshotToDict(timeStamp, batchID, DissolvedOxygen, Temperature, pH, Yield, AlarmTriggered, AlarmType)


def evaluateAlarms(do: float, temp: float, ph: float) -> tuple[bool, str]:
    """
    Check all process variables for alarm conditions.
    
    Returns:
        alarm_triggered (bool): True if any alarm tripped.
        alarm_types (str): Comma-separated list of alarms or ''.
    """
    alarms = []

    if do < DO_LOW_THRESHOLD or do > DO_HIGH_THRESHOLD:
        alarms.append("DOOutOfRange")
    if temp > TEMP_HIGH_THRESHOLD:
        alarms.append("HighTemp")
    if ph < PH_LOW_THRESHOLD or ph > PH_HIGH_THRESHOLD:
        alarms.append("pHOutOfRange")

    alarm_triggered = len(alarms) > 0
    alarm_types = ", ".join(alarms) if alarms else ""

    return alarm_triggered, alarm_types

def getYield(alarmsTriggered: bool, alarmType: str) -> float:
    """Calculate yield based on alarm condition penalty."""

    baseYield = random.uniform(3.6, 3.8)  # (g)
    alarmCount = alarmType.count(",") + 1 if alarmType else 0
    penalty = random.uniform(1, 2) * alarmCount 
    return max(baseYield - penalty, 0.0)


def snapshotToDict(time: str, batchID: int, do: float, temp: float, ph: float, productYield: float, alarmsTriggered: bool, alarmType: str) -> dict:
    """Convert multiple values to a dictionary"""
    snapshot = {
        "Timestamp": time,
        "BatchID": batchID,
        "DissolvedOxygen": round(do, 1),
        "Temperature": round(temp, 1),
        "pH": round(ph, 2),
        "Yield": round(productYield, 2),
        "AlarmTriggered": int(alarmsTriggered),
        "AlarmType": alarmType
    }
    return snapshot


def appendSnapshot(snapshot: dict, filePath: str = DATA_FILE_PATH):
    """Append a new snapshot to the CSV file."""
    try:
        df = pd.DataFrame([snapshot])
        df.to_csv(filePath, mode="a", header=False, index=False)
    except Exception as e:
        #print(f"[ERROR] Failed to append snapshot: {e}")
        pass


if __name__ == "__main__":
    runSimulatorLoop()