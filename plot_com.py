
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to calculate velocity from position data
def calculate_velocity(data):
    return np.diff(data, axis=0)

# Function to create side-by-side line plots for position and velocity for each component
def create_side_by_side_plots(data1_pos, data2_pos, data1_vel, data2_vel):
    num_frames_pos = np.arange(data1_pos.shape[0])
    num_frames_vel = np.arange(data1_vel.shape[0])
    
    # Define colors for each data source
    color_mediapipe = 'blue'
    color_yolo = 'red'

    # Create subplots
    fig = make_subplots(rows=3, cols=2, subplot_titles=["X Position", "X Velocity", "Y Position", "Y Velocity", "Z Position", "Z Velocity"])

    # Add traces for position and velocity for x, y, z components
    for i in range(3):
        fig.add_trace(go.Scatter(x=num_frames_pos, y=data1_pos[:, i], mode='lines', name='Mediapipe' if i == 0 else '', line=dict(color=color_mediapipe), opacity=.5), row=i+1, col=1)
        fig.add_trace(go.Scatter(x=num_frames_pos, y=data2_pos[:, i], mode='lines', name='Yolo' if i == 0 else '', line=dict(color=color_yolo), opacity=.3), row=i+1, col=1)
        fig.add_trace(go.Scatter(x=num_frames_vel, y=data1_vel[:, i], mode='lines', name='Mediapipe' if i == 0 else '', line=dict(color=color_mediapipe), opacity=.5), row=i+1, col=2)
        fig.add_trace(go.Scatter(x=num_frames_vel, y=data2_vel[:, i], mode='lines', name='Yolo' if i == 0 else '', line=dict(color=color_yolo), opacity=.3), row=i+1, col=2)

    # Update layout
    fig.update_layout(height=900, width=1200, title_text="COM Position and Velocity for X, Y, Z")
    fig.show()

data1 = np.load(Path(r'D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\mediapipe_MDN_Trial_3_yolo\mediapipe_output_data\center_of_mass\total_body_center_of_mass_xyz.npy'))
data2 = np.load(Path(r"D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\mediapipe_MDN_Trial_3_yolo\output_data\center_of_mass\total_body_center_of_mass_xyz.npy"))
# Calculate velocity for both datasets
velocities1 = calculate_velocity(data1)
velocities2 = calculate_velocity(data2)

# Plot COM position data
create_side_by_side_plots(data1, data2, velocities1, velocities2)

