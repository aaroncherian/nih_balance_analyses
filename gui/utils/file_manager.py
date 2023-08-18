from pathlib import Path
from PyQt6.QtWidgets import  QFileDialog
import numpy as np
from gui.utils.mediapipe_skeleton_builder import mediapipe_indices, qualisys_indices

class FileManager:
    def __init__(self):
        self.data_options = {
            "freemocap": {
                "marker_data_array_name": "mediapipe_body_3d_xyz.npy",
                "markers_to_use": mediapipe_indices
            },
            "qualisys": {
                "marker_data_array_name": "clipped_qualisys_skel_3d.npy",
                "markers_to_use": qualisys_indices
            }
        }
        
        self.session_folder_path = None

    def get_existing_directory(self, dialog_title="Choose a session"):
        folder_diag = QFileDialog()
        self.session_folder_path = QFileDialog.getExistingDirectory(None, dialog_title)
        self.session_folder_path = Path(self.session_folder_path)
        return self.session_folder_path if self.session_folder_path else None

    def load_skeleton_data(self, session_folder_path, marker_data_array_name):
        skeleton_data_folder_path = session_folder_path / 'output_data' / marker_data_array_name
        return np.load(skeleton_data_folder_path)
    
    
    def load_center_of_mass_data(self, session_folder_path):
        """Load the center of mass data from the given session folder path."""
        try:
            path_to_total_body_COM_data = session_folder_path / 'output_data' / 'center_of_mass' / 'total_body_center_of_mass_xyz.npy'
            total_body_COM_data = np.load(path_to_total_body_COM_data)
            return total_body_COM_data, None  # Return the data and None for error message
        except Exception as e:
            return None, str(e)  # Return None for data and the error message

    def get_data_option(self, option_name):
        return self.data_options.get(option_name)