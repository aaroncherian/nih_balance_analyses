
from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QHBoxLayout,QVBoxLayout, QPushButton, QFileDialog, QRadioButton, QGroupBox,QTabWidget

from gui.widgets.skeleton_view_widget import SkeletonViewWidget
from gui.widgets.slider_widget import FrameCountSlider
from gui.widgets.video_capture_widget import VideoDisplay
from gui.widgets.frame_marking_widget import FrameMarker
from gui.widgets.saving_data_analysis_widget import SavingDataAnalysisWidget
from gui.widgets.balance_assessment_widget import BalanceAssessmentWidget
from utils.mediapipe_skeleton_builder import build_skeleton, mediapipe_connections, mediapipe_indices, qualisys_indices
from gui.models.results_container import BalanceAssessmentResultsContainer

from gui.plots.path_length_line_plot import PathLengthsPlot
from gui.plots.com_postion_and_velocity_plot import PositionAndVelocityPlot

from pathlib import Path

import numpy as np

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
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        self.results_container = BalanceAssessmentResultsContainer(condition_frame_dictionary={}, path_length_dictionary={}, velocity_dictionary={}, postion_dictionary={}, center_of_mass_xyz = None)

        self.tab_widget = QTabWidget()

        self.main_tab = MainTab(self.results_container)
        self.tab_widget.addTab(self.main_tab, "Main Menu")

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        self.connect_signals_to_slots()

    def connect_signals_to_slots(self):
        self.main_tab.balance_assessment_widget.balance_assessment_finished_signal.connect(self.add_path_lengths_plot_tab)
        self.main_tab.balance_assessment_widget.balance_assessment_finished_signal.connect(self.add_position_and_velocity_plot_tab)

    def add_path_lengths_plot_tab(self):
        # Instantiate the plotting widget and plot the data
        path_lengths_plot_widget = PathLengthsPlot()
        path_lengths_plot_widget.plot_data(self.results_container)

        # Add the plotting widget as a new tab
        self.tab_widget.addTab(path_lengths_plot_widget, "Path Length vs. Condition")

    def add_position_and_velocity_plot_tab(self):
        # Instantiate the plotting widget and plot the data
        position_and_velocity_plot_widget = PositionAndVelocityPlot()
        position_and_velocity_plot_widget.plot_data(self.results_container)

        # Add the plotting widget as a new tab
        self.tab_widget.addTab(position_and_velocity_plot_widget, "Position and Velocity vs. Condition")






class MainTab(QWidget):

    def __init__(self, results_container):
        super().__init__()

        self.setWindowTitle("My App")

        layout = QVBoxLayout(self) 

        self.file_manager = FileManager()
        self.results_container = results_container
        

        slider_and_skeleton_layout = QVBoxLayout()

        self.load_session_groupbox = self.create_load_session_groupbox()
        slider_and_skeleton_layout.addWidget(self.load_session_groupbox)

        self.skeleton_viewer_groupbox = self.create_skeleton_viewer_groupbox()
        slider_and_skeleton_layout.addWidget(self.skeleton_viewer_groupbox)

        self.camera_view_groupbox = self.create_camera_view_groupbox()
        self.frame_marking_groupbox = self.create_frame_marking_groupbox()
        self.balance_assessment_groupbox = self.create_balance_assessment_groupbox()
        self.saving_data_groupbox = self.create_saving_data_groupbox()

        main_layout = QHBoxLayout()
        main_layout.addLayout(slider_and_skeleton_layout)
        main_layout.addWidget(self.camera_view_groupbox)

        layout.addLayout(main_layout)
        layout.addWidget(self.frame_marking_groupbox)
        layout.addWidget(self.balance_assessment_groupbox)
        layout.addWidget(self.saving_data_groupbox)

        self.setLayout(layout) 

        self.connect_signals_to_slots()

    def connect_signals_to_slots(self):
        self.frame_count_slider.slider.valueChanged.connect(self.handle_slider_value_changed)
        self.camera_view_widget.video_loader.video_loaded_signal.connect(self.set_video_to_slider_frame)

        self.frame_marking_widget.conditions_dict_updated_signal.connect(lambda: self.balance_assessment_widget.set_condition_frames_dictionary(self.frame_marking_widget.condition_widget_dictionary))
    

    def _handle_session_folder_loaded(self):
        self.frame_count_slider.set_slider_range(self.num_frames)
        self.enable_buttons()
        self.set_session_folder_path()

    def handle_slider_value_changed(self):
        self.skeleton_view_widget.replot(self.frame_count_slider.slider.value())
        if self.camera_view_widget.video_loader.video_is_loaded:
            current_frame = self.frame_count_slider.slider.value()
            self.camera_view_widget.set_frame(current_frame)


    def set_video_to_slider_frame(self):
        current_frame = self.frame_count_slider.slider.value()
        self.camera_view_widget.set_frame(current_frame)

    def open_folder_dialog(self):
        self.session_folder_path = self.file_manager.get_existing_directory("Choose a session")

        if self.session_folder_path:

            if self.freemocap_radio.isChecked():
                marker_data_array_name = 'mediapipe_body_3d_xyz.npy'
                markers_to_use = mediapipe_indices
            elif self.qualisys_radio.isChecked():
                marker_data_array_name = 'clipped_qualisys_skel_3d.npy'
                markers_to_use = qualisys_indices

            self.skel3d_data = self.file_manager.load_skeleton_data(self.session_folder_path, marker_data_array_name)
            self.build_mediapipe_skeleton(markers_to_use)

            com_data, error_msg = self.file_manager.load_center_of_mass_data(self.session_folder_path)
            if not error_msg:
                self.balance_assessment_widget.set_center_of_mass_data(com_data)
                self.results_container.center_of_mass_xyz = com_data

    def build_mediapipe_skeleton(self, markers_to_use:list):

        self.mediapipe_skeleton = build_skeleton(self.skel3d_data,markers_to_use,mediapipe_connections)
        self.num_frames = self.skel3d_data.shape[0]
        self.skeleton_view_widget.reset_skeleton_3d_plot(self.skel3d_data, self.mediapipe_skeleton)
        self._handle_session_folder_loaded()
    
    def set_session_folder_path(self):
        self.camera_view_widget.video_loader.set_session_folder_path(self.session_folder_path)
    
    def enable_buttons(self):
        self.balance_assessment_widget.run_path_length_analysis_button.setEnabled(True)
        self.camera_view_widget.video_loader.videoLoadButton.setEnabled(True)
        self.frame_marking_widget.save_condition_button.setEnabled(True)
        self.frame_marking_widget.load_conditions_button.setEnabled(True)
        self.saving_data_widget.save_data_button.setEnabled(True)

    def set_condition_frames_dictionary(self, condition_frames_dictionary:dict):
        self.condition_frames_dictionary = condition_frames_dictionary

    def create_load_session_groupbox(self):
        groupbox = QGroupBox("Load a Session")
        load_session_layout = QVBoxLayout()

        self.freemocap_radio = QRadioButton('Load FreeMoCap Data')
        self.freemocap_radio.setChecked(True)
        load_session_layout.addWidget(self.freemocap_radio)
        self.qualisys_radio = QRadioButton('Load Qualisys Data')
        load_session_layout.addWidget(self.qualisys_radio)
        
        self.folder_open_button = QPushButton('Load a session folder', self)
        self.folder_open_button.clicked.connect(self.open_folder_dialog)
        load_session_layout.addWidget(self.folder_open_button)
        groupbox.setLayout(load_session_layout)

        return groupbox
    
    def create_skeleton_viewer_groupbox(self):
        
        groupbox = QGroupBox("View Skeleton")
        view_skeleton_layout = QVBoxLayout()
        self.frame_count_slider = FrameCountSlider()
        view_skeleton_layout.addWidget(self.frame_count_slider)
        self.skeleton_view_widget = SkeletonViewWidget()
        self.skeleton_view_widget.setFixedSize(self.skeleton_view_widget.size())
        view_skeleton_layout.addWidget(self.skeleton_view_widget)
        
        groupbox.setLayout(view_skeleton_layout)

        return groupbox

    def create_camera_view_groupbox(self):
        groupbox = QGroupBox("Load a Video")
        layout = QVBoxLayout()
        self.camera_view_widget = VideoDisplay()
        self.camera_view_widget.setFixedSize(self.skeleton_view_widget.size())
        layout.addWidget(self.camera_view_widget)
        groupbox.setLayout(layout)
        return groupbox

    def create_frame_marking_groupbox(self):
        groupbox = QGroupBox("Annotate Frames for Conditions")
        layout = QVBoxLayout()
        self.frame_marking_widget = FrameMarker()
        self.frame_marking_widget.setFixedSize(640,200)
        layout.addWidget(self.frame_marking_widget)
        groupbox.setLayout(layout)
        return groupbox

    def create_balance_assessment_groupbox(self):
        groupbox = QGroupBox("Run Balance Assessment")
        layout = QVBoxLayout()
        self.balance_assessment_widget = BalanceAssessmentWidget(self.results_container)
        layout.addWidget(self.balance_assessment_widget)
        groupbox.setLayout(layout)
        return groupbox

    def create_saving_data_groupbox(self):
        groupbox = QGroupBox("Save Data")
        layout = QVBoxLayout()
        self.saving_data_widget = SavingDataAnalysisWidget(self.file_manager, self.results_container)
        layout.addWidget(self.saving_data_widget)
        groupbox.setLayout(layout)
        return groupbox
    

if __name__ == "__main__":

    app = QApplication([])
    win = MainWindow()

    win.show()
    app.exec()
