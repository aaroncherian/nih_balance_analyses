from freemocap_utils.freemocap_data_loader import FreeMoCapDataLoader
from PyQt6.QtWidgets import QWidget,QVBoxLayout, QPushButton, QLabel
from freemocap_utils.GUI_widgets.NIH_widgets.balance_thread_worker import BalanceAssessmentWorkerThread

import numpy as np

from pathlib import Path
import json

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PyQt6.QtCore import pyqtSignal

class BalanceAssessmentWidget(QWidget):
    run_button_clicked_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.balance_assessment_worker = None
        self.total_body_COM_data = None
        self.condition_frames_dictionary = None

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self.run_path_length_analysis_button = QPushButton('Run balance assessment')
        self.run_path_length_analysis_button.clicked.connect(self.run_COM_analysis)
        self.run_path_length_analysis_button.setEnabled(False)
        self._layout.addWidget(self.run_path_length_analysis_button)

        self.path_length_results = QLabel()
        self._layout.addWidget(self.path_length_results)

    def run_COM_analysis(self):
        self.start_balance_assessment()
    
    def start_balance_assessment(self):
        if self.total_body_COM_data is None or self.condition_frames_dictionary is None:
            # Handle the case where the necessary data isn't loaded yet.
            return
        
        task_list = ['calculate_path_lengths', 'calculate_velocities']

        self.balance_assessment_worker = BalanceAssessmentWorkerThread(
            com_data=self.total_body_COM_data,
            condition_frames_dictionary=self.condition_frames_dictionary,
            task_list=task_list,
            all_tasks_finished_callback=self.on_balance_assessment_completed
        )


        self.balance_assessment_worker.start()

    def on_balance_assessment_completed(self, task_results):
        self.path_length_dictionary = task_results['calculate_path_lengths']['result']
        self.velocity_dictionary = task_results['calculate_velocities']['result']

        self.path_length_results.setText(str(self.path_length_dictionary))

        f = 2
        
    def set_conditions_frames_dictionary(self, condition_frames_dictionary:dict):
        self.condition_frames_dictionary = condition_frames_dictionary

    def set_center_of_mass_data(self, com_data):
        """Set the center of mass data for the widget."""
        self.total_body_COM_data = com_data
