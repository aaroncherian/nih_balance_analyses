import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path 
from freemocap_utils.mediapipe_skeleton_builder import mediapipe_indices

import plotly.graph_objects as go
from plotly.subplots import make_subplots


class FileManager:
    def __init__(self, path_to_session_folder, path_to_data_analysis):
        self.path_to_session_folder = path_to_session_folder
        self.path_to_data_analysis = path_to_data_analysis

        self.output_data_folder = 'output_data'
        self.marker_data_array_name = 'mediapipe_body_3d_xyz.npy'
        self.com_data_array_name = 'total_body_center_of_mass_xyz.npy'

    def load_skeleton_data(self, path_to_session_folder):
        skeleton_data_folder_path = path_to_session_folder / self.output_data_folder  / self.marker_data_array_name
        return np.load(skeleton_data_folder_path)
    
    def load_com_data(self,path_to_session_folder):
        com_folder_path = path_to_session_folder/self.output_data_folder/'center_of_mass'/self.com_data_array_name
        return np.load(com_folder_path)
    
    def load_condition_slices(self, path_to_data_analysis):

        self.marker_data_3d = self.load_skeleton_data(path_to_session_folder=self.path_to_session_folder)
        self.com_data_3d = self.load_com_data(path_to_session_folder=self.path_to_session_folder)

        condition_json_path = path_to_data_analysis/'condition_data.json'
        condition_slices = json.load(open(condition_json_path))

        conditions_names = list(condition_slices['Frame Intervals'].keys())
        conditions_slices = list(condition_slices['Frame Intervals'].values())

        marker_data_sliced = {}
        for condition_name, condition_slice in zip(conditions_names, conditions_slices):
            marker_data_sliced[condition_name] = self.marker_data_3d[condition_slice[0]:condition_slice[1]]

        com_data_sliced = {}
        for condition_name, condition_slice in zip(conditions_names, conditions_slices):
            com_data_sliced[condition_name] = self.com_data_3d[condition_slice[0]:condition_slice[1]]

        return marker_data_sliced,com_data_sliced
        f = 2
    
    def save_figure(self, figure, filename):
        figure.savefig(self.path_to_data_analysis / filename)

class COM_2D_Plotter:
    def __init__(self, path_to_session_folder, path_to_data_analysis):
        self.path_to_session_folder = path_to_session_folder

        self.file_manager = FileManager(path_to_session_folder=path_to_session_folder, path_to_data_analysis=path_to_data_analysis)

        self.condition_slices = self.file_manager.load_condition_slices(path_to_data_analysis)
        self.marker_data_sliced, self.com_data_sliced = self.file_manager.load_condition_slices(path_to_data_analysis)

    def create_2D_COM_plot(self, mediapipe_indices):
        # List of conditions for indexing
        conditions = ['Eyes Open/Solid Ground', 'Eyes Closed/Solid Ground', 'Eyes Open/Foam', 'Eyes Closed/Foam']

        ax_range = 165  # Set the range for each axis

        fig = make_subplots(rows=2, cols=2, subplot_titles=conditions, shared_yaxes=False)

        for i, condition in enumerate(conditions):
            # Get COM and marker data for the current condition
            com_data = self.com_data_sliced[condition]
            marker_data = self.marker_data_sliced[condition]

            # Extract x and y positions for COM
            com_x = com_data[:, 0]
            com_y = com_data[:, 1]

            # Get indices for left and right heel and foot_index
            left_heel_index = mediapipe_indices.index('left_heel')
            right_heel_index = mediapipe_indices.index('right_heel')
            left_foot_index = mediapipe_indices.index('left_foot_index')
            right_foot_index = mediapipe_indices.index('right_foot_index')

            # Extract x and y positions for feet
            left_heel_x = np.mean(marker_data[:, left_heel_index, 0])
            left_heel_y = np.mean(marker_data[:, left_heel_index, 1])
            right_heel_x = np.mean(marker_data[:, right_heel_index, 0])
            right_heel_y = np.mean(marker_data[:, right_heel_index, 1])
            left_foot_x = np.mean(marker_data[:, left_foot_index, 0])
            left_foot_y = np.mean(marker_data[:, left_foot_index, 1])
            right_foot_x = np.mean(marker_data[:, right_foot_index, 0])
            right_foot_y = np.mean(marker_data[:, right_foot_index, 1])

            # Calculate average position between the average positions of the left and right feet
            ref_point_x = (left_heel_x + right_heel_x + left_foot_x + right_foot_x) / 4
            ref_point_y = (left_heel_y + right_heel_y + left_foot_y + right_foot_y) / 4

            # Plot COM as a line with transparency
            fig.add_trace(go.Scatter(x=com_x, y=com_y, mode='lines', name='COM', line=dict(color='black', width=1), opacity=0.5, showlegend=(i==0)), row=i//2+1, col=i%2+1)

            # Plot average foot positions
            fig.add_trace(go.Scatter(x=[left_heel_x, left_foot_x], y=[left_heel_y, left_foot_y], mode='lines+markers', name='Left Foot', line=dict(color='blue', width=1), showlegend=(i==0)),  row=i//2+1, col=i%2+1)
            fig.add_trace(go.Scatter(x=[right_heel_x, right_foot_x], y=[right_heel_y, right_foot_y], mode='lines+markers', name='Right Foot', line=dict(color='red', width=1), showlegend=(i==0)),  row=i//2+1, col=i%2+1)

            # Set axis range using the average foot position as reference point
            fig.update_xaxes(range=[ref_point_x - ax_range, ref_point_x + ax_range],  row=i//2+1, col=i%2+1)
            fig.update_yaxes(range=[ref_point_y - ax_range, ref_point_y + ax_range],  row=i//2+1, col=i%2+1)

        fig.update_yaxes(title_text = 'Y Axis (mm)', row=1, col=1)
        fig.update_yaxes(title_text = 'Y Axis (mm)', row=2, col=1)

        fig.update_xaxes(title_text = 'X Axis (mm)', row=2, col=1)
        fig.update_xaxes(title_text = 'X Axis (mm)', row=2, col=2)


        fig.update_layout(title_text="Center of Mass (COM) Trajectory and Foot Positions", width = 650, height = 650, showlegend=True, yaxis_scaleanchor="x", template="plotly_white",)

        # Save the plot as an HTML file
        # fig.write_html(str(self.file_manager.path_to_data_analysis / "com_dispersion_plots.html"))
        # fig.write_html(str(r'C:\Users\aaron\Documents\GitHub\nih_balance_analyses\docs\images\com_dispersion_plots.html'))
        fig.show()


if __name__ == "__main__":

    path_to_session_folder = Path(r'D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\sesh_2023-05-17_15_03_20_MDN_NIH_Trial4')
    path_to_data_analysis = Path(r'D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\sesh_2023-05-17_15_03_20_MDN_NIH_Trial4\data_analysis\analysis_2023-06-01_10_17_22')
    
    com_2d_plotter = COM_2D_Plotter(path_to_session_folder=path_to_session_folder, path_to_data_analysis=path_to_data_analysis)
    com_2d_plotter.create_2D_COM_plot(mediapipe_indices)




