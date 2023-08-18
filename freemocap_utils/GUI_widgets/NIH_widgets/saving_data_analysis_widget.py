from pathlib import Path
import datetime
import json

import pandas as pd
import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton,
                             QFormLayout, QLabel)


class SavingDataAnalysisWidget(QWidget):
    def __init__(self, file_manager, results_container):
        super().__init__()

        self.results_container = results_container
        self.file_manager = file_manager
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components."""
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self._saved_folder_name_entry = QLineEdit()
        self._saved_folder_name_entry.setMaximumWidth(200)
        self._saved_folder_name_entry.setText(
            datetime.datetime.now().strftime("analysis_%Y-%m-%d_%H_%M_%S")
        )

        saved_folder_name_form = QFormLayout()
        saved_folder_name_form.addRow(QLabel('ID for data analysis folder'), 
                                      self._saved_folder_name_entry)
        self._layout.addLayout(saved_folder_name_form)

        self.save_data_button = QPushButton('Save out data analysis results')
        self.save_data_button.clicked.connect(self._save_data_out)
        self.save_data_button.setEnabled(False)
        self._layout.addWidget(self.save_data_button)

    def _format_data_json(self, condition_frame_intervals_dictionary, 
                          path_length_dictionary):
        """Format the data into JSON format."""
        return {
            'Frame Intervals': condition_frame_intervals_dictionary, 
            'Path Lengths:': path_length_dictionary
        }

    def _create_dataframe_from_dict(self, data_dict):
        """Create a dataframe from the provided dictionary."""
        dataframes = []

        for condition, arrays in data_dict.items():
            for dimension, arr in zip(['x', 'y', 'z'], arrays):
                temp_df = pd.DataFrame({f"{condition}_{dimension}": arr})
                dataframes.append(temp_df)

        # Concatenate all dataframes horizontally
        result_df = pd.concat(dataframes, axis=1)
        result_df['Frame'] = np.arange(len(result_df))
        return result_df

    def _create_folder_to_save_data(self, saved_folder_name):
        """Create a folder to save the data."""
        saved_data_analysis_path = (self.file_manager.session_folder_path / 
                                    'data_analysis' / saved_folder_name)
        saved_data_analysis_path.mkdir(parents=True, exist_ok=True)
        return saved_data_analysis_path

    def _save_data_json(self, dict_for_json, json_name, save_folder_path):
        """Save the data as a JSON file."""
        json_file_name = save_folder_path / json_name
        with open(json_file_name, 'w') as out_file:
            json.dump(dict_for_json, out_file, indent=1)

    def _save_plot(self, figure, file_name, save_folder_path):
        """Save the figure as a plot."""
        figure.savefig(str(save_folder_path / file_name))

    def _save_data_out(self):
        """Save the data analysis results."""
        saved_folder_name = self._saved_folder_name_entry.text()
        saved_data_analysis_path = self._create_folder_to_save_data(saved_folder_name)
        formatted_condition_data_dict = self._format_data_json(
            self.results_container.condition_frame_dictionary,
            self.results_container.path_length_dictionary
        )
        self._save_data_json(formatted_condition_data_dict, 
                             'condition_data.json', 
                             saved_data_analysis_path)
        self._save_velocity_dict_as_csv(self.results_container.velocity_dictionary,
                                        saved_data_analysis_path)
        self._save_position_dict_as_csv(self.results_container.position_dictionary,
                                        saved_data_analysis_path)
        self._save_plot(self.results_container.path_length_figure,
                        'path_length_plot.png', saved_data_analysis_path)
        self._save_plot(self.results_container.position_and_velocity_figure,
                        'position_and_velocity_plot.png', saved_data_analysis_path)

    def _save_velocity_dict_as_csv(self, velocity_dict, save_folder_path):
        """Save the velocity data as a CSV."""
        velocity_dataframe = self._create_dataframe_from_dict(velocity_dict)
        velocity_dataframe.to_csv(save_folder_path / 'condition_velocities.csv', 
                                  index=False)

    def _save_position_dict_as_csv(self, position_dict, save_folder_path):
        """Save the position data as a CSV."""
        position_dataframe = self._create_dataframe_from_dict(position_dict)
        position_dataframe.to_csv(save_folder_path / 'condition_positions.csv', 
                                  index=False)
