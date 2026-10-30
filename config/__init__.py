
import pandas as pd
import zipfile
import gzip
import io
from pathlib import Path

BASE = Path(r"D:\CampusOptimizer")
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)

# Convert energy Excel to CSV
energy = pd.read_excel(
    BASE / "hourly load profile of NITPY.xlsx",
    sheet_name="Sheet1",
    header=None
)
energy.columns = ["load"]
energy.to_csv(DATA / "energy.csv", index=False)

# Extract traffic CSV from ZIP
with zipfile.ZipFile(
    BASE / "metro+interstate+traffic+volume.zip"
) as archive:
    filename = next(
        name for name in archive.namelist()
        if name.lower().endswith((".csv", ".csv.gz"))
    )
    content = archive.read(filename)

    if filename.lower().endswith(".gz"):
        content = gzip.decompress(content)

traffic = pd.read_csv(io.BytesIO(content))
traffic.to_csv(DATA / "traffic.csv", index=False)

print("Energy CSV created:", len(energy), "rows")
print("Traffic CSV created:", len(traffic), "rows")
print("Files saved inside:", DATA)
