
import io
import gzip
import zipfile
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

ENERGY_FILE = (
    BASE_DIR / "hourly load profile of NITPY.xlsx"
)

TRAFFIC_FILE = (
    BASE_DIR / "metro+interstate+traffic+volume.zip"
)


def get_energy_summary():
    if not ENERGY_FILE.is_file():
        raise FileNotFoundError(
            f"Energy dataset missing: {ENERGY_FILE}"
        )

    df = pd.read_excel(
        ENERGY_FILE,
        sheet_name="Sheet1",
        header=None
    )

    readings = pd.to_numeric(
        df.iloc[:, 0],
        errors="coerce"
    )

    valid = readings.dropna()

    if valid.empty:
        raise ValueError("No valid energy readings.")

    return {
        "source": "NITPY hourly load workbook",
        "total_rows": len(df),
        "valid_readings": len(valid),
        "missing_readings": int(readings.isna().sum()),
        "average_load": round(float(valid.mean()), 2),
        "minimum_load": round(float(valid.min()), 2),
        "maximum_load": round(float(valid.max()), 2),
        "units_verified": False,
        "timestamps_verified": False
    }


def get_traffic_summary():
    if not TRAFFIC_FILE.is_file():
        raise FileNotFoundError(
            f"Traffic dataset missing: {TRAFFIC_FILE}"
        )

    with zipfile.ZipFile(TRAFFIC_FILE) as archive:
        files = [
            name for name in archive.namelist()
            if name.lower().endswith((".csv", ".csv.gz"))
        ]

        if not files:
            raise ValueError(
                "No CSV dataset found inside ZIP."
            )

        filename = files[0]
        raw = archive.read(filename)

        if filename.lower().endswith(".gz"):
            raw = gzip.decompress(raw)

        df = pd.read_csv(io.BytesIO(raw))

    if "traffic_volume" not in df.columns:
        raise ValueError("traffic_volume column missing.")

    df["traffic_volume"] = pd.to_numeric(
        df["traffic_volume"],
        errors="coerce"
    )

    volume = df["traffic_volume"].dropna()

    if volume.empty:
        raise ValueError("No valid traffic observations.")

    peak_hour = None

    if "date_time" in df.columns:
        timestamps = pd.to_datetime(
            df["date_time"],
            errors="coerce"
        )

        hourly = pd.DataFrame({
            "hour": timestamps.dt.hour,
            "volume": df["traffic_volume"]
        }).dropna()

        if not hourly.empty:
            hourly_average = hourly.groupby(
                "hour"
            )["volume"].mean()

            peak_hour = int(hourly_average.idxmax())

    return {
        "source": "Historical interstate traffic dataset",
        "total_records": len(df),
        "valid_volume_records": len(volume),
        "average_volume": round(float(volume.mean()), 2),
        "minimum_volume": float(volume.min()),
        "maximum_volume": float(volume.max()),
        "peak_hour": peak_hour,
        "campus_data_verified": False
    }
