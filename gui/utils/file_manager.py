from pathlib import Path
from PyQt6.QtWidgets import  QFileDialog
import numpy as np
from gui.utils.mediapipe_skeleton_builder import mediapipe_indices, qualisys_indices

class FileManager:
    def __init__(self):
        self.session_folder_path = None

    def scan_session_for_data(self, session_folder_path: str|Path):
        session_folder_path = Path(session_folder_path)
        path_to_validation_folder = session_folder_path / 'validation'

        valid_datasets = [f for f in path_to_validation_folder.iterdir() if f.is_dir() and any(f.glob("*.parquet"))]
        return valid_datasets

    def get_existing_directory(self, dialog_title="Choose a session"):
        folder_diag = QFileDialog()
        self.session_folder_path = QFileDialog.getExistingDirectory(None, dialog_title)
        self.session_folder_path = Path(self.session_folder_path)
        return self.session_folder_path if self.session_folder_path else None

    def load_skeleton_data(self, data_folder_path, marker_data_array_name):
        skeleton_data_folder_path = data_folder_path / marker_data_array_name
        return np.load(skeleton_data_folder_path)
    