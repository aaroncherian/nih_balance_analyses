import matplotlib
# matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
import json
import numpy as np
import seaborn as sns

import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
        if 'sesh' in str(path_to_analysis_folder).lower(): #this is a freemocap folder
            freemocap_path_lengths.append(pd.DataFrame(json_data['Path Lengths:'], index=[0]))
        elif 'qualisys' in str(path_to_analysis_folder).lower():
            qualisys_path_lengths.append(pd.DataFrame(json_data['Path Lengths:'], index=[0]))

    # Concatenate DataFrames
    freemocap_path_lengths = pd.concat(freemocap_path_lengths)
    qualisys_path_lengths = pd.concat(qualisys_path_lengths)

    return freemocap_path_lengths, qualisys_path_lengths

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

freemocap_path_lengths, qualisys_path_lengths = aggregate_path_lengths(analysis_folders)

sns.set_style('whitegrid')

# Calculate mean and standard deviation
freemocap_mean = freemocap_path_lengths.mean()
freemocap_std = freemocap_path_lengths.std()

qualisys_mean = qualisys_path_lengths.mean()
qualisys_std = qualisys_path_lengths.std()

# Conditions
conditions = freemocap_mean.index
conditions = [condition.replace('/', '\n') for condition in conditions]

# Create figure with subplots
fig = make_subplots(rows=1, cols=2, subplot_titles=("Freemocap", "Qualisys"), shared_yaxes=True)

# Add individual lines for Freemocap
for index, row in freemocap_path_lengths.iterrows():
    fig.add_trace(
        go.Scatter(x=conditions, y=row, mode='lines+markers', line=dict(color='#7994B0', width=0.5), showlegend=False),
        row=1, col=1
    )

# Add mean line with error bars for Freemocap
fig.add_trace(
    go.Scatter(x=conditions, y=freemocap_mean, mode='lines+markers', error_y=dict(type='data', array=freemocap_std, visible=True),
               line=dict(color='black'), name='Mean'),
    row=1, col=1
)

# Add individual lines for Qualisys
for index, row in qualisys_path_lengths.iterrows():
    fig.add_trace(
        go.Scatter(x=conditions, y=row, mode='lines+markers', line=dict(color='#C67548', width=0.5), showlegend=False),
        row=1, col=2
    )

# Add mean line with error bars for Qualisys
fig.add_trace(
    go.Scatter(x=conditions, y=qualisys_mean, mode='lines+markers', error_y=dict(type='data', array=qualisys_std, visible=True),
               line=dict(color='black'), name='Mean'),
    row=1, col=2
)

# Update layout
fig.update_layout(height=600, width=700, title_text="Path Length Comparison", template = 'plotly_white')
fig.update_yaxes(title_text="Path Length (mm)", row=1, col=1)
fig.update_xaxes(title_text="Condition", row=1, col=1)
fig.update_xaxes(title_text="Condition", row=1, col=2)

# Show figure
# fig.show()

fig.write_html(str(r'C:\Users\aaron\Documents\GitHub\nih_balance_analyses\docs\images\path_length_line_plots.html'), full_html=False, include_plotlyjs='cdn')