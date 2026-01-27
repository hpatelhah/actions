import pandas as pd
from datetime import datetime

df = pd.DataFrame({
    "status": ["GitHub Actions works"],
    "timestamp": [datetime.utcnow().isoformat()]
})

df.to_excel("test_report.xlsx", index=False)

print("Excel file created successfully")
