import numpy as np
import pandas as pd

# 1) Set up the time axis
#    10 seconds total, sampling every 5 ms => 0.005 s
time = np.arange(0, 10, 0.005)  # => 0.0, 0.005, 0.01, ..., up to < 10

# 2) Create the Voltage signal
#    Centered at 5, with a 60 Hz sinusoidal noise term and small random noise
voltage = (
    5.0
    + 0.2 * np.sin(2 * np.pi * 60 * time)   # 60 Hz noise
    + 0.01 * np.random.randn(len(time))     # small random noise
)

# 3) Create X, Y, Z position data
#    All are 0.5 Hz sine waves, each centered at a different level (150, 75, 100)
#    and each offset by a different phase so they are out of sync
x_position = 150.0 + 10.0 * np.sin(2 * np.pi * 0.5 * time + 0.0)
y_position =  75.0 + 10.0 * np.sin(2 * np.pi * 0.5 * time + 2 * np.pi / 3)
z_position = 100.0 + 10.0 * np.sin(2 * np.pi * 0.5 * time + 4 * np.pi / 3)

# 4) Combine into a Pandas DataFrame
df_synthetic = pd.DataFrame({
    "time": time,
    "Voltage": voltage,
    "X_position": x_position,
    "Y_position": y_position,
    "Z_position": z_position
})

# 5) (Optional) Preview the first few rows
print(df_synthetic.head())

# 6) Save data in multiple formats for testing:
#    CSV, TXT, and Excel

# CSV
df_synthetic.to_csv("synthetic_data.csv", index=False)

# TXT (tab-delimited)
df_synthetic.to_csv("synthetic_data.txt", sep="\t", index=False)

# Excel
df_synthetic.to_excel("synthetic_data.xlsx", sheet_name="Sheet1", index=False)
