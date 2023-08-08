import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
import json
import numpy as np
import seaborn as sns

def aggregate_path_lengths(analysis_folders):
    # Lists to store path lengths
    freemocap_path_lengths = []
    qualisys_path_lengths = []

    # Process each analysis folder
    for path_to_analysis_folder in analysis_folders:
        # Check if path exists
        if not Path(path_to_analysis_folder).exists():
            print(f"Path {path_to_analysis_folder} does not exist.")
            continue
        
        # Load JSON file
        json_name = 'condition_data.json'
        json_path = path_to_analysis_folder / json_name
        
        # Check if JSON file exists
        if not json_path.exists():
            print(f"JSON file not found in {path_to_analysis_folder}.")
            continue

        # Read the JSON data
        with open(json_path, 'r') as file:
            json_data = json.load(file)
        
        # Extract and store path lengths (assuming JSON structure is known)

        freemocap_path_lengths.append(pd.DataFrame(json_data['Path Lengths:'], index=[0]))

    # Concatenate DataFrames
    freemocap_path_lengths = pd.concat(freemocap_path_lengths)


    return freemocap_path_lengths



analysis_folders = [
    Path(r"D:\2023-07-26_SBT002\1.0_recordings\calib_1\sesh_2023-07-26_14_19_10_STB002_NIH_Trial1\data_analysis\analysis_2023-08-04_15_37_33"),
    Path(r"D:\2023-07-26_SBT002\1.0_recordings\calib_1\sesh_2023-07-26_14_40_40_STB002_NIH_Trial2\data_analysis\analysis_2023-08-04_15_49_28"),
    Path(r"D:\2023-07-26_SBT002\1.0_recordings\calib_1\sesh_2023-07-26_14_49_52_STB002_NIH_Trial3\data_analysis\analysis_2023-08-08_10_49_53")
]

freemocap_path_lengths = aggregate_path_lengths(analysis_folders)

sns.set_style('whitegrid')

# Calculate mean and standard deviation
freemocap_mean = freemocap_path_lengths.mean()
freemocap_std = freemocap_path_lengths.std()

# Conditions
conditions = freemocap_mean.index
conditions = [condition.replace('/', '\n') for condition in conditions]

# Create figure with subplots
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

# Plotting Freemocap data
for index, row in freemocap_path_lengths.iterrows():
    ax.plot(conditions, row, '-o', color= '#7994B0', alpha=0.5)

# Adding Freemocap mean and error bars
ax.errorbar(conditions, freemocap_mean, yerr=freemocap_std, fmt='-o', color='black', capsize=5, label='Mean')

# Labels and titles for Freemocap
ax.set_title('Freemocap', fontsize = 16)
ax.set_ylabel('Path Length (mm)', fontsize = 14)
ax.legend(loc = 'upper left')
ax.set_xlabel('Condition', fontsize = 14)

# Display the plot
plt.tight_layout()
plt.show()