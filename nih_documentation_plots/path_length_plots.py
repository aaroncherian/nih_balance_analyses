import matplotlib
matplotlib.use("Qt5Agg")
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
        json_data = json.load(open(json_path))

        # Extract and store path lengths (assuming JSON structure is known)
        if 'sesh' in str(path_to_analysis_folder).lower(): #this is a freemocap folder
            freemocap_path_lengths.append(pd.DataFrame(json_data['Path Lengths:'], index=[0]))
        elif 'qualisys' in str(path_to_analysis_folder).lower():
            qualisys_path_lengths.append(pd.DataFrame(json_data['Path Lengths:'], index=[0]))

    # Concatenate DataFrames
    freemocap_path_lengths = pd.concat(freemocap_path_lengths)
    qualisys_path_lengths = pd.concat(qualisys_path_lengths)

    # Calculate mean and standard deviation
    freemocap_mean = freemocap_path_lengths.mean()
    freemocap_std = freemocap_path_lengths.std()

    qualisys_mean = qualisys_path_lengths.mean()
    qualisys_std = qualisys_path_lengths.std()

    return freemocap_mean, freemocap_std, qualisys_mean, qualisys_std

# Example usage
analysis_folders = [
    Path(r'D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\sesh_2023-05-17_14_40_56_MDN_NIH_Trial2\data_analysis\analysis_2023-06-01_10_03_59'),
    Path(r'D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\sesh_2023-05-17_14_53_48_MDN_NIH_Trial3\data_analysis\analysis_2023-06-01_10_12_24'),
    Path(r'D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\sesh_2023-05-17_15_03_20_MDN_NIH_Trial4\data_analysis\analysis_2023-06-01_10_17_22'),
    Path(r'D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\qualisys_MDN_NIH_Trial2\data_analysis\analysis_2023-06-01_16_11_00'),
    Path(r'D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\qualisys_MDN_NIH_Trial3\data_analysis\analysis_2023-06-01_17_14_40'),
    Path(r'D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\qualisys_MDN_NIH_Trial4\data_analysis\analysis_2023-06-01_18_06_59')
    # ... more paths
]

freemocap_mean, freemocap_std, qualisys_mean, qualisys_std = aggregate_path_lengths(analysis_folders)
# Combine data into a single DataFrame
data = []
conditions = freemocap_mean.index

# Add freemocap data
for condition, mean, std in zip(conditions, freemocap_mean, freemocap_std):
    data.append(['Freemocap', condition, mean, std])

# Add qualisys data
for condition, mean, std in zip(conditions, qualisys_mean, qualisys_std):
    data.append(['Qualisys', condition, mean, std])

# Create DataFrame
df = pd.DataFrame(data, columns=['System', 'Condition', 'Mean Path Length', 'Standard Deviation'])

n_conditions = len(df['Condition'].unique())

# Setting the width of the bars and position of the labels
bar_width = 0.35
index = np.arange(n_conditions)

# Plotting the barplot
plt.figure(figsize=(10, 6))

# Plot Freemocap bars
plt.bar(index, df[df['System'] == 'Freemocap']['Mean Path Length'],
        bar_width, label='Freemocap',
        yerr=df[df['System'] == 'Freemocap']['Standard Deviation'],
        capsize=5, alpha=0.8)

# Plot Qualisys bars
plt.bar(index + bar_width, df[df['System'] == 'Qualisys']['Mean Path Length'],
        bar_width, label='Qualisys',
        yerr=df[df['System'] == 'Qualisys']['Standard Deviation'],
        capsize=5, alpha=0.8)

# Adding labels and title
plt.xlabel('Condition')
plt.ylabel('Mean Path Length')
plt.title('Comparison of Mean Path Lengths Between Freemocap and Qualisys')
plt.xticks(index + bar_width / 2, df['Condition'].unique())
plt.legend(title='System')

# Display the plot
plt.show()