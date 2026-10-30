
from pathlib import Path
from datetime import datetime, timezone
import gzip
import io
import zipfile

import pandas as pd
from fastapi import FastAPI, HTTPException

from backend.agent_api import router as agent_router


BASE_DIR = Path(__file__).resolve().parent.parent

TRAFFIC_FILE = BASE_DIR / "metro+interstate+traffic+volume.zip"
ENERGY_FILE = BASE_DIR / "hourly load profile of NITPY.xlsx"


app = FastAPI(
    title="AURIX QUANTUM Backend API",
    description="Campus Energy and Traffic Intelligence Backend",
    version="3.0.0"
)

app.include_router(agent_router)


def load_traffic():
    if not TRAFFIC_FILE.exists():
        raise FileNotFoundError(
            f"Traffic dataset not found: {TRAFFIC_FILE}"
        )

    with zipfile.ZipFile(TRAFFIC_FILE, "r") as archive:
        files = [
            name for name in archive.namelist()
            if name.lower().endswith((".csv", ".csv.gz"))
        ]

        if not files:
            raise ValueError("No CSV dataset found inside ZIP.")

        filename = files[0]
        data = archive.read(filename)

        if filename.lower().endswith(".gz"):
            data = gzip.decompress(data)

        df = pd.read_csv(io.BytesIO(data))

    required = {"date_time", "traffic_volume"}

    if not required.issubset(df.columns):
        raise ValueError("Traffic dataset columns are missing.")

    df["date_time"] = pd.to_datetime(
        df["date_time"], errors="coerce"
    )

    df["traffic_volume"] = pd.to_numeric(
        df["traffic_volume"], errors="coerce"
    )

    df = df.dropna(
        subset=["date_time", "traffic_volume"]
    ).copy()

    if df.empty:
        raise ValueError("No valid traffic records.")

    df["hour"] = df["date_time"].dt.hour

    return df


def load_energy():
    if not ENERGY_FILE.exists():
        raise FileNotFoundError(
            f"Energy dataset not found: {ENERGY_FILE}"
        )

    df = pd.read_excel(
        ENERGY_FILE,
        sheet_name="Sheet1",
        header=None
    )

    values = pd.to_numeric(
        df.iloc[:, 0],
        errors="coerce"
    ).dropna().reset_index(drop=True)

    if values.empty:
        raise ValueError("No valid energy readings.")

    result = pd.DataFrame({
        "load": values
    })

    result["hour"] = result.index % 24

    return result


def traffic_summary_data():
    df = load_traffic()

    hourly = (
        df.groupby("hour")["traffic_volume"]
        .mean()
        .round(2)
    )

    return {
        "source": "Historical interstate traffic dataset",
        "total_records": int(len(df)),
        "average_volume": round(
            float(df["traffic_volume"].mean()), 2
        ),
        "maximum_volume": float(
            df["traffic_volume"].max()
        ),
        "peak_hour": int(hourly.idxmax()),
        "hourly_average": {
            str(int(hour)): float(value)
            for hour, value in hourly.items()
        }
    }


def energy_summary_data():
    df = load_energy()

    hourly = (
        df.groupby("hour")["load"]
        .mean()
        .round(3)
    )

    return {
        "source": "NITPY hourly load workbook",
        "total_readings": int(len(df)),
        "average_load": round(
            float(df["load"].mean()), 2
        ),
        "maximum_load": float(df["load"].max()),
        "minimum_load": float(df["load"].min()),
        "peak_indexed_hour": int(hourly.idxmax()),
        "units_verified": False,
        "timestamps_verified": False,
        "hourly_average": {
            str(int(hour)): float(value)
            for hour, value in hourly.items()
        }
    }


@app.get("/", tags=["System"])
def home():
    return {
        "project": "AURIX QUANTUM",
        "message": "Campus Energy and Traffic Optimizer",
        "backend_version": "3.0.0",
        "status": "online"
    }


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "traffic_dataset_exists": TRAFFIC_FILE.exists(),
        "energy_dataset_exists": ENERGY_FILE.exists()
    }


@app.get("/agents", tags=["System"])
def list_agents():
    return {
        "project": "AURIX QUANTUM",
        "agents": [
            "Data Quality Agent",
            "Traffic Analyst",
            "Energy Analyst",
            "Groq AI Coordinator",
            "Rule-Based Verification Agent"
        ],
        "execution_endpoint": "POST /agents/run"
    }


@app.get("/traffic/summary", tags=["Traffic"])
def traffic_summary():
    try:
        return traffic_summary_data()
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )


@app.get("/energy/summary", tags=["Energy"])
def energy_summary():
    try:
        return energy_summary_data()
    except (OSError, ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )


@app.get("/analytics/overview", tags=["Analytics"])
def analytics_overview():
    try:
        traffic = traffic_summary_data()
        energy = energy_summary_data()

        return {
            "project": "AURIX QUANTUM",
            "status": "analysis_completed",
            "traffic": {
                "records": traffic["total_records"],
                "average_volume": traffic["average_volume"],
                "peak_hour": traffic["peak_hour"]
            },
            "energy": {
                "readings": energy["total_readings"],
                "average_load": energy["average_load"],
                "peak_indexed_hour": energy["peak_indexed_hour"]
            },
            "analysis_type": "Historical data analysis"
        }

    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )
