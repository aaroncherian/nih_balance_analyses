import plotly.graph_objects as go
from plotly.subplots import make_subplots

import numpy as np
import json
from pathlib import Path

path_to_data_folder = Path(r'D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3')

data_folder = 'output_data'
center_of_mass_folder = 'center_of_mass'
total_body_com_file = 'total_body_center_of_mass_xyz.npy'
analysis_folder = 'data_analysis'

sessionIDs = ['sesh_2023-05-17_14_40_56_MDN_NIH_Trial2']

colors = ['blue', 'green', 'red']
dimensions = ['X', 'Y', 'Z']

# For each session, load data and plot
for j, sessionID in enumerate(sessionIDs):
    # Load center of mass data
    com_file_path = path_to_data_folder / sessionID / data_folder / center_of_mass_folder / total_body_com_file
    com_data = np.load(com_file_path)

    # Load condition_data.json
    analysis_subfolders = sorted((path_to_data_folder / sessionID / analysis_folder).glob('analysis_*'))
    if not analysis_subfolders:
        print(f"No analysis subfolders found for session {sessionID}")
        continue
    condition_json_path = analysis_subfolders[-1] / 'condition_data.json'
    with open(condition_json_path, 'r') as file:
        condition_data = json.load(file)
    
    # Extract frame intervals for 'Eyes Open/Solid Ground'
    frame_intervals = condition_data["Frame Intervals"]["Eyes Open/Solid Ground"]
    start_frame, end_frame = frame_intervals

    # Create a figure with subplots
    fig = make_subplots(rows=2, cols=2, shared_xaxes=True, 
                    subplot_titles=("COM X Position", "COM Y Position", "COM X Velocity", "COM Y Velocity"))


    # Extract the x, y data for the given frames
    for i in range(2):
        # Position
        pos_data = com_data[100:10000, i]
        fig.add_trace(go.Scatter(y=pos_data, mode='lines', line=dict(color=colors[i]), name=f'{dimensions[i]} Position'), row=1, col=i+1)
        # Velocity
        vel_data = np.diff(com_data[100:10000, i])
        fig.add_trace(go.Scatter(y=vel_data, mode='lines', line=dict(color=colors[i]), name=f'{dimensions[i]} Velocity'), row=2, col=i+1)

    # Update axes labels and titles
    for i in range(2):
        # fig.update_xaxes(title_text='Frame #', row=1, col=i+1)
        fig.update_yaxes(title_text='Position (mm)', row=1, col=i+1)
        fig.update_xaxes(title_text='Frame #', row=2, col=i+1)
        fig.update_yaxes(title_text='Velocity (mm/frame)', row=2, col=i+1)

    # Update subplot titles
    fig.update_layout(
        title=f'Trial {j+1} COM',
        showlegend=False,
        template='plotly_white'
    )

    # Show plot
fig.show()

fig.write_html(str(r'C:\Users\aaron\Documents\GitHub\nih_balance_analyses\docs\images\com_position_and_velocity.html'), full_html=False, include_plotlyjs='cdn')