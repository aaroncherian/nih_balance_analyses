

from PyQt6.QtWidgets import QWidget,QVBoxLayout, QLineEdit, QPushButton ,QFormLayout, QLabel

from pathlib import Path
import json

import datetime

import pandas as pd

class SavingDataAnalysisWidget(QWidget):
    def __init__(self, file_manager, results_container):
        super().__init__()

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self.results_container = results_container
        self.file_manager = file_manager

        self.saved_folder_name_entry = QLineEdit()
        self.saved_folder_name_entry.setMaximumWidth(200)
        self.saved_folder_name_entry.setText(datetime.datetime.now().strftime("analysis_%Y-%m-%d_%H_%M_%S"))
        
        saved_folder_name_form = QFormLayout()
        saved_folder_name_form.addRow(QLabel('ID for data analysis folder'), self.saved_folder_name_entry)
        self._layout.addLayout(saved_folder_name_form)  

        self.save_data_button = QPushButton('Save out data analysis results')
        self.save_data_button.clicked.connect(self.save_data_out)
        self.save_data_button.setEnabled(False)
        self._layout.addWidget(self.save_data_button)



    def format_data_json(self,condition_frame_intervals_dictionary, path_length_dictionary):
        dict_to_save = {'Frame Intervals':condition_frame_intervals_dictionary, 'Path Lengths:': path_length_dictionary}
        return dict_to_save

    def save_data_out(self):
        saved_folder_name = self.saved_folder_name_entry.text()
        self.saved_data_analysis_path = self.create_folder_to_save_data(saved_folder_name)
        formatted_condition_data_dict = self.format_data_json(self.results_container.condition_frame_dictionary,self.results_container.path_length_dictionary)
        self.save_data_json(formatted_condition_data_dict, 'condition_data.json', self.saved_data_analysis_path)
        self.save_velocity_dict_as_csv(self.results_container.velocity_dictionary,self.saved_data_analysis_path)
        self.save_position_dict_as_csv(self.results_container.position_dictionary,self.saved_data_analysis_path)
        # self.save_plot(self.histogram_figure,self.saved_data_analysis_path)


    # def save_conditions_dict(self, conditions_dictionary:dict):
    #     saved_folder_name = self.saved_folder_name_entry.text()
    #     self.saved_data_analysis_path = self.create_folder_to_save_data(saved_folder_name)

    #     self.create_frame_interval_json(conditions_dictionary,self.saved_data_analysis_path)


    def create_folder_to_save_data(self, saved_folder_name:str):

        saved_data_analysis_path = self.file_manager.session_folder_path/'data_analysis'/saved_folder_name
        saved_data_analysis_path.mkdir(parents = True, exist_ok=True)

        return saved_data_analysis_path


    def save_data_json(self,dict_for_json:dict, json_name:str, save_folder_path:Path):
        json_file_name = save_folder_path/json_name
        out_file = open(json_file_name,'w')

        json.dump(dict_for_json,out_file, indent=1)


    def save_velocity_dict_as_csv(self, velocity_dict:dict, save_folder_path:Path):
        velocity_dataframe = self._create_dataframe_from_dict(velocity_dict)
        velocity_dataframe.to_csv(save_folder_path/'condition_velocities.csv', index=False)

    def save_position_dict_as_csv(self, position_dict:dict, save_folder_path:Path):
        position_dataframe = self._create_dataframe_from_dict(position_dict)
        position_dataframe.to_csv(save_folder_path/'condition_positions.csv', index=False)

    def _create_dataframe_from_dict(self, data_dict:dict):
        data_frames = []
        for count, dimension in enumerate(['x', 'y', 'z']):
            this_dimension_array_list = [item[count] for item in data_dict.values()]
            conditions_list = list(data_dict.keys())
            this_dimension_dict = dict(zip(conditions_list, this_dimension_array_list))
            df = pd.DataFrame(this_dimension_dict)
            df['Dimension'] = dimension
            data_frames.append(df)
        
        combined_df = pd.concat(data_frames).reset_index()
        combined_df = combined_df.rename(columns={"index": "Frame"})
        return combined_df
        

    def save_plot(self,figure,save_folder_path:Path):
        figure.savefig(str(save_folder_path/'velocity_histogram.png'))


