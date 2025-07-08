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
SIMULATION_INTERVAL_SEC = 1

DO_HIGH_THRESHOLD = 50.0
DO_LOW_THRESHOLD = 20.0
TEMP_HIGH_THRESHOLD = 40.0
PH_LOW_THRESHOLD = 6.5
PH_HIGH_THRESHOLD = 7.5

# -------------------------------------
# Core Functions
# -------------------------------------

def runSimulatorLoop(batchCount: int = 100):
    """
    - Generate fake timestamp, process variables, alarm conditions
    - Append row to data/batch_data.csv
    """
    initializeCSV()
    for count in range(batchCount):
        snapshot = generateProcessSnapshot(count+1)
        appendSnapshot(snapshot)
        time.sleep(SIMULATION_INTERVAL_SEC)
    print(f"Simulating process... {snapshot}")

def initializeCSV(filePath: str = DATA_FILE_PATH):
    """Ensure /data exists, then wipe CSV and write header row."""
    os.makedirs(os.path.dirname(filePath), exist_ok=True)
    with open(filePath, mode="w") as f:
        f.write("Timestamp,BatchID,DissolvedOxygen,Temperature,pH,AlarmTriggered,AlarmType(s)\n")


def generateProcessSnapshot(batchID: int) -> dict:
    """Generate a single process snapshot with timestamp and variable values."""
    Timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    DissolvedOxygen = random.uniform(18, 55) #(%)
    Temperature = random.uniform(35, 42)    #(°C)
    pH = random.uniform(6.0, 8.0)
    AlarmTriggered, AlarmType = evaluateAlarms(DissolvedOxygen, Temperature, pH)
    return snapshotToDict(Timestamp, batchID, DissolvedOxygen, Temperature, pH, AlarmTriggered, AlarmType)


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


def snapshotToDict(time: str, batchID: int, do: float, temp: float, ph: float, alarmsTriggered: bool, alarmType: str) -> dict:
    """Convert multiple values to a dictionary"""
    snapshot = {
        "Timestamp": time,
        "BatchID": batchID,
        "DissolvedOxygen": round(do, 2),
        "Temperature": round(temp, 2),
        "pH": round(ph, 2),
        "AlarmTriggered": int(alarmsTriggered),
        "AlarmType": alarmType
    }
    return snapshot


def appendSnapshot(snapshot: dict, file_path: str = DATA_FILE_PATH):
    """Append a new snapshot to the CSV file."""
    try:
        df = pd.DataFrame([snapshot])
        df.to_csv(file_path, mode="a", header=False, index=False)
    except Exception as e:
        print(f"[ERROR] Failed to append snapshot: {e}")


if __name__ == "__main__":
    runSimulatorLoop()