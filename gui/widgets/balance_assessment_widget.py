from PyQt6.QtWidgets import QWidget,QVBoxLayout, QPushButton, QLabel
from gui.widgets.balance_thread_worker import BalanceAssessmentWorkerThread

from PyQt6.QtCore import pyqtSignal

class BalanceAssessmentWidget(QWidget):
    run_button_clicked_signal = pyqtSignal()
    balance_assessment_finished_signal = pyqtSignal()

    def __init__(self, balance_results_container):
        super().__init__()
        
        self.balance_results_container = balance_results_container

        self.balance_assessment_worker = None
        self.total_body_COM_data = None

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
        if self.total_body_COM_data is None or self.balance_results_container.condition_frame_dictionary is None:
            # Handle the case where the necessary data isn't loaded yet.
            return
        
        task_list = ['calculate_path_lengths', 'calculate_velocities', 'splice_positions_by_condition']


        self.balance_assessment_worker = BalanceAssessmentWorkerThread(
            com_data=self.total_body_COM_data,
            condition_frames_dictionary=self.balance_results_container.condition_frame_dictionary,
            task_list=task_list,
            all_tasks_finished_callback=self.on_balance_assessment_completed
        )


        self.balance_assessment_worker.start()

    def on_balance_assessment_completed(self, task_results):
        self.path_length_dictionary = task_results['calculate_path_lengths']['result']
        self.velocity_dictionary = task_results['calculate_velocities']['result']
        self.position_dictionary = task_results['splice_positions_by_condition']['result']

        self.path_length_results.setText(str(self.path_length_dictionary))

        self.balance_results_container.path_length_dictionary = self.path_length_dictionary
        self.balance_results_container.velocity_dictionary = self.velocity_dictionary
        self.balance_results_container.position_dictionary = self.position_dictionary

        self.balance_assessment_finished_signal.emit()
        f = 2

    def set_center_of_mass_data(self, com_data):
        """Set the center of mass data for the widget."""
        self.total_body_COM_data = com_data
